# Plotting functions to be used in notebooks
"""
#Debugging setup for VS Code
import os
os.chdir("..")
import KAPy
os.chdir("..")
config=KAPy.getConfig("./config/config.yaml")  
wf=KAPy.getWorkflow(config)
"""

from plotnine import *
import pandas as pd
import os
import xarray as xr
import matplotlib

# Set default backend to workaround problems caused by the
# default not being uniform across systems - in particular, we 
# hit a problem with micromamba vs conda having different defaults.
# This lead to a crashes when running in a non-Gui environment
matplotlib.use('Agg')

# Boxplot---------------------------------------------------------------------------
"""
indID="101"
srcFiles=list(wf['plots'].values())[0]
srcFiles=['results/5.areal_statistics/101_CORDEX_rcp26_ensstats.csv',
          'results/5.areal_statistics/101_CORDEX_rcp85_ensstats.csv']
"""

def makeBoxplot(config, indID, srcFiles, outFile=None):
    # Extract indicator info
    thisInd = config["indicators"][indID]

    # Load csv files as panadas dataframes
    # Note that we need to make sure that we read the ID's as strings
    dat = []
    for f in srcFiles:
        datIn = pd.read_csv(f)
        datIn["fname"] = os.path.basename(f)
        datIn["periodID"] = [str(x) for x in datIn["periodID"]]
        datIn["scenario"] = datIn["fname"].str.extract("^.*?_.*?_(.*?)_.*$")
        dat += [datIn]
    datdf = pd.concat(dat)

    # Get metafra data from configuration
    ptileTbl = (
        pd.DataFrame.from_dict(
            config["ensembles"], orient="index", columns=["percentiles"]
        )
        .reset_index()
        .rename(columns={"index": "ptileLbl"})
    )
    periodTbl = pd.DataFrame.from_dict(config["periods"], orient="index")
    periodLblDict = {
        x["id"]: f"{x['name']}\n({x['start']}-{x['end']})"
        for i, x in periodTbl.iterrows()
    }
    scTbl = pd.DataFrame.from_dict(config["scenarios"], orient="index")
    scColourDict = {x["id"]: "#" + x["hexcolour"] for i, x in scTbl.iterrows()}

    # Now merge into dataframe and pivot for plotting
    pltLong = pd.merge(datdf, ptileTbl, on="percentiles", how="left")
    pltDatWide = pltLong.pivot_table(
        index=["scenario", "periodID"], columns="ptileLbl", values="indicator"
    ).reset_index()

    # Now plot
    p = (
        ggplot(pltDatWide)
        + geom_boxplot(
            mapping=aes(
                x="periodID",
                fill="scenario",
                middle="centralPercentile",
                ymin="lowerPercentile",
                ymax="upperPercentile",
                lower="lowerPercentile",
                upper="upperPercentile",
            ),
            width=0.5,
            stat="identity",
        )
        + labs(
            x="Period",
            y=f"Value ({thisInd['units']})",
            title=f"{thisInd['name']} ",
            fill="Scenario",
        )
        + scale_x_discrete(labels=periodLblDict)
        + scale_fill_manual(values=scColourDict)
        + theme_bw()
        + theme(legend_position="bottom", panel_grid_major_x=element_blank())
    )

    # Output
    if outFile is not None:
        p.save(outFile[0],
               verbose=False)
    return p


# Spatialplot -----------------------------------------------------------
"""
indID='101'
srcFiles=list(wf['plots'].values())[1]
"""


# def makeSpatialplot(config, indID, srcFiles, outFile=None):
#     # Extract indicator info
#     thisInd = config["indicators"][indID]

#     # Read netcdf files using xarray and calculate difference
#     datdf = []
#     for d in srcFiles:
#         # Import object
#         thisdat = xr.open_dataset(d)

#         # We want to plot a spatial map of the change from start to finish
#         change = thisdat.isel(periodID=-1) - thisdat.isel(periodID=0)
#         changedf = change.indicator_mean.to_dataframe().reset_index()
#         changedf["fname"] = os.path.basename(d)
#         changedf["scenario"] = changedf["fname"].str.extract("^.*?_.*?_(.*?)_.*$")
#         datdf += [changedf]
#     pltDat = pd.concat(datdf)

#     # Make plot
#     p = (
#         ggplot(pltDat, aes(x="lon", y="lat", fill="indicator_mean"))
#         + geom_raster()
#         + facet_wrap("~scenario")
#         + theme_bw()
#         + labs(
#             x="",
#             y="",
#             fill=f"Change\n({thisInd['units']})",
#             title=f"{thisInd['name']} ",
#             caption="Change in indicator from first period to last period",
#         )
#         + scale_x_continuous(expand=[0, 0])
#         + scale_y_continuous(expand=[0, 0])
#         + theme(legend_position="bottom")
#         + coord_fixed()
#     )

#     # Output
#     if outFile is not None:
#         p.save(outFile[0],
#                verbose=False)
#     return p


# Lineplot------------------------------------------------------------------
"""
indID=101
srcFiles=list(wf['plots'].values())[0]
"""


def makeLineplot(config, indID, srcFiles, outFile=None):
    # Extract indicator info
    thisInd = config["indicators"][indID]

    # Load csv files as panadas dataframes
    dat = []
    for f in srcFiles:
        datIn = pd.read_csv(f)
        datIn["fname"] = os.path.basename(f)
        datIn["scenario"] = datIn["fname"].str.extract("^.*?_.*?_(.*?)_.*$")
        dat += [datIn]
    datdf = pd.concat(dat)
    datdf["datetime"] = pd.to_datetime(datdf["time"])

    # Get metafra data from configuration
    scTbl = pd.DataFrame.from_dict(config["scenarios"], orient="index")
    scColourDict = {x["id"]: f"#{x["hexcolour"]}" for i, x in scTbl.iterrows()}

    # Now select data for plotting - we only plot the central value, not the full range
    pltDat = datdf[datdf["percentiles"] == config["ensembles"]["centralPercentile"]]

    # Now plot
    plot = (
        ggplot(pltDat, aes(x="datetime", y="indicator", colour="scenario"))
        + geom_line()
        + labs(
            x="",
            y=f"Value ({thisInd['units']})",
            title=f"{thisInd['name']} ",
            colour="Scenario",
        )
        + scale_colour_manual(values=scColourDict)
        + theme_bw()
        + theme(legend_position="bottom")
    )
    # Output
    if outFile is not None:
        plot.save(outFile[0],
               verbose=False)
    return plot
