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
    change_ds_list = []
    historical_mean_value = ds_historical["indicator_mean"].isel(periodID=0).drop("periodID")

    for period in range(1, n_periods):
        current_ds = xr.Dataset(ds.isel(periodID=period) - ds_historical.isel(periodID=0)).expand_dims("periodID")
        current_change = current_ds["indicator_mean"].isel(periodID=0)
        change_ds_list.append(current_ds.assign(indicator_mean_rel = xr.DataArray(current_change*100/historical_mean_value).expand_dims("periodID")))

    change_ds = xr.concat(change_ds_list, "periodID")

    change_ds["periodID"].astype("int")
    attrs = ds.attrs
    attrs["units"] = indicator["units"]
    attrs["name"] = indicator["name"]
    attrs["scenario"] =  scenario
    change_ds = change_ds.assign_attrs(attrs)
    change_ds = change_ds["indicator_mean_rel"].assign_attrs({"units": "%"})

    change_ds.to_netcdf(netcdf_filename[0])