# USDA crop insurance analysis
The purpose of this repository is to:
1. provide a reliable way to download USDA crop insurance data from the Risk Management Agency website
2. look into the USDA crop insurance loss patterns for different crops and regions

## Data sources
### Crop insurance
Crop insurance data was downloaded from the USDA's Risk Management Agency (RMA) [State/County/Crop Summary of Business](https://www.rma.usda.gov/tools-reports/summary-of-business/state-county-crop-summary-business) site.

### Administrative boundaries
National, state, and county boundaries for CONUS were downloaded from Natural Earth data hosted by the [North American Cartographic Information Society](https://nacis.org/initiatives/natural-earth/).


## Coding environment
To recreate the coding environment we use in this repository, please run:
```
mamba env create -f environment.yaml
```
And to activate the environment:
```
mamba activate crop_insurance
```

## Code structure
In order to run the Jupyter Notebooks for the different crops, we first need to download and process the crop insurance data. There are a few Python scripts in `src/` that set up the data you will need to replicate the analyses and figures in this repository.

### USDA RMA crop insurance statistics
The first is the Python script that scrapes annual crop insurance statistics:
```
python3 src/download_crop_insurance_data.py
```

By default, this script assumes that you want to download all the crop insurance data that is available (1948 - 2026). If you only want to download or process data for a particular time period, you can use the `-sy` and `-ey` (or `--start_year` and `--end-year`) flags.

Here is how you would download crop insurance data from 2015 through the present:
```
python3 src/download_crop_insurance_data.py -sy 2015
```

**Note**: the crop insurance data from 1948-1988 is in a single, consolidated `TXT` file. It is not possible (at least with this download script) to download individual years of data within this time period.

Once the raw crop insurance data is downloaded, you can then process the downloaded `TXT` files and combine them into a single `Parquet` file.
```
python3 src/process_crop_insurance_data.py
```

This script looks for all text files that are available, so there is no need to specify start and end years.

### USDA crop insurance data
After the crop insruance data has been downloaded, you can run each of the Jupyter Notebooks for `corn`, `cotton`, and `soy` in `notebooks/`.


## Acknowledgements
This repository was inspired by the [EWG's Farm Subsidy Database](https://farm.ewg.org/cropinsurance.php?fips=00000&summpage=IN_BY_YEAR&regionname=theUnitedStates) and [Rock Creek Analytics' report](https://www.rockcreekanalytics.com/modeling-crop-insurance-claims/) on crop insurance claims.

The EWG site is great, but doesn't currently allow you to filter data by combining crops, years, states, and cause of loss. Instead, you need to choose one, so this repository allowed me to filter and combine data in a more flexible way.

In the Rock Creek Analytics report, the data is presented together for all crops and states in a static PDF. I wanted to be able to look at individual crops and states to tease out more interesting trends in insurance claims. Still, the outline of the Jupyter Notebooks for each crop follows their report outline closely.
