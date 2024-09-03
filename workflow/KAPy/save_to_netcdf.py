import pandas as pd
import os
import xarray as xr

# Save cahnges from first period to rcp scenarios to netcdf --------------------------------------------------------------------------
"""
indicator_id = "102"
ensemble_stats_files = [/lustre/storeC-ext/users/klimakverna/development/Klimakverna-pilot-KAPy/KAPy/results/4.ensstats/time_binning_periods/hadgem/102_CMIP5_historical_ensstats.nc,
                        /lustre/storeC-ext/users/klimakverna/development/Klimakverna-pilot-KAPy/KAPy/results/4.ensstats/time_binning_periods/hadgem/102_CMIP5_rcp26_ensstats.nc,
                        /lustre/storeC-ext/users/klimakverna/development/Klimakverna-pilot-KAPy/KAPy/results/4.ensstats/time_binning_periods/hadgem/102_CMIP5_rcp45_ensstats.nc
                        ]

output_files = [/lustre/storeC-ext/users/klimakverna/development/Klimakverna-pilot-KAPy/KAPy/results/7.netcdf/102_rcp26_change_periods.nc]
"""

def save_to_netcdf(config, indicator_id, scenario, ensemble_stats_files, netcdf_filename=None):

    indicator = config["indicators"][indicator_id]

    for filename in ensemble_stats_files:
        if scenario in filename:
            ds = xr.open_dataset(filename)
        elif "historical" in filename:
            ds_historical = xr.open_dataset(filename)
    
    n_periods = len(config["periods"])
    change_ds = xr.Dataset()

    for period in range(1, n_periods):
        change_ds = xr.concat([ds.isel(periodID=period) - ds_historical.isel(periodID=0), change_ds], "periodID")

    change_ds["periodID"].astype("int")
    attrs = ds.attrs
    attrs["units"] = indicator["units"]
    attrs["name"] = indicator["name"]
    attrs["scenario"] =  scenario
    change_ds = change_ds.assign_attrs(attrs)

    change_ds.to_netcdf(netcdf_filename[0])
    

    #     changedf = change.indicator_mean.to_dataframe().reset_index()
    #     changedf["fname"] = os.path.basename(filename)
    #     changedf["scenario"] = changedf["fname"].str.extract("^.*?_.*?_(.*?)_.*$")
    #     changes_dataframes += [changedf]
    # pltDat = pd.concat(changes_dataframes)

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
