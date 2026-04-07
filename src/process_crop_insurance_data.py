import sys
from pathlib import Path

import numpy as np
import pandas as pd


def process_crop_insurance_data():
    """
    This script processes crop insurance data that has been downloaded from the USDA's Risk Management Agency site:
    https://www.rma.usda.gov/tools-reports/summary-of-business/state-county-crop-summary-business

    The data is split into two parts, one from 1948 - 1988 and the other from 1989 - present.
    They are formatted slightly differently, with the earlier time period's data being a consolidated
    text file, whereas data after 1988 is in individual text files.
    """

    SCRIPT_DIR = Path(__file__).resolve().parent  # ./src
    PROJECT_ROOT = SCRIPT_DIR.resolve().parent  # .. project root
    INPUT_DIR = PROJECT_ROOT / 'data' / 'raw'
    OUTPUT_DIR = PROJECT_ROOT / 'data' / 'processed'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    filenames_list = sorted([str(path) for path in list(INPUT_DIR.glob('*.txt'))])

    # set start and end year variables for filename when saving combined output
    if '1948' in filenames_list[0]:
        start_year = 1948
    else:
        start_year = filenames_list[0][-8:-4]

    if '1948' in filenames_list[-1]:
        end_year = 1948
    else:
        end_year = filenames_list[-1][-8:-4]

    # first, process consolidated data from 1948 - 1988
    # https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/SOB_State_County_Commodity_1948_1988.pdf
    columns = [
        'commodity_year',
        'state_code',
        'state',
        'fips',
        'county_name',
        'commodity_code',
        'commodity_name',
        'policies_sold',
        'policies_premium',
        'policies_indemnified',
        'units_premium',
        'units_indemnified',
        'net_quantity',
        'liability',
        'total_premium',
        'subsidy',
        'indemnity',
        'loss_ratio',
    ]

    data_list = []

    filenames = [filename for filename in filenames_list if '1948' in filename]
    print()
    for filename in filenames:
        print('Processing data for: 1948 - 1988')

        with open(filename) as f:
            lines = [line.replace('\n', '') for line in f]

        for line in lines:
            tokens = line.split('|')
            tokens = [token.lstrip().rstrip() for token in tokens]

            # make sure no data is missing
            assert len(tokens) == len(columns)
            data_list.append(tokens)

    # create dataframe from list of values
    insurance_1948_1988 = pd.DataFrame({})
    for idx, col in enumerate(columns):
        insurance_1948_1988[col] = [tokens[idx] for tokens in data_list]

    # convert numeric columns
    int_cols = ['commodity_year', 'policies_sold', 'policies_premium', 'policies_indemnified']
    float_cols = [
        'units_premium',
        'units_indemnified',
        'net_quantity',
        'liability',
        'total_premium',
        'subsidy',
        'indemnity',
        'loss_ratio',
    ]

    for col in int_cols:
        insurance_1948_1988[col] = insurance_1948_1988[col].astype('Int64')

    for col in float_cols:
        insurance_1948_1988[col] = insurance_1948_1988[col].astype(float)

    # next, process individual, annual TXT files for data from 1989 - present
    # https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop/SOB_State_County_Crop_with_Coverage_Level_1989_Forward.pdf
    columns = [
        'commodity_year',
        'state_code',
        'state',
        'fips',
        'county_name',
        'commodity_code',
        'commodity_name',
        'insurance_code',
        'insurance_name',
        'coverage_category',
        'delivery_type',
        'coverage_level',
        'policies_sold',
        'policies_premium',
        'policies_indemnified',
        'units_premium',
        'units_indemnified',
        'quantity_type',
        'net_quantity',
        'endorsed_acres',
        'liability',
        'total_premium',
        'subsidy',
        'state_private_subsidy',
        'additional_subsidy',
        'efa_premium_discount',
        'indemnity',
        'loss_ratio',
    ]

    data_list = []

    filenames = [filename for filename in filenames_list if '1948' not in filename]
    for filename in filenames:
        year = int(filename[-8:-4])
        print(f'Processing data for: {year}')

        with open(filename) as f:
            lines = [line.replace('\n', '') for line in f]

            for line in lines:
                tokens = line.split('|')
                tokens = [token.lstrip().rstrip() for token in tokens]

                # make sure no data is missing
                assert len(tokens) == len(columns)
                data_list.append(tokens)

    # create dataframe from list of values
    insurance_1989_2026 = pd.DataFrame({})
    for idx, col in enumerate(columns):
        insurance_1989_2026[col] = [tokens[idx] for tokens in data_list]

    # convert numeric columns
    int_cols = ['commodity_year', 'policies_sold', 'policies_premium', 'policies_indemnified']
    float_cols = [
        'units_premium',
        'units_indemnified',
        'net_quantity',
        'endorsed_acres',
        'liability',
        'total_premium',
        'subsidy',
        'state_private_subsidy',
        'additional_subsidy',
        'efa_premium_discount',
        'indemnity',
        'loss_ratio',
    ]

    for col in int_cols + float_cols:
        # we need to replace '' values with np.nan so we can convert them to numeric datatype in the dataframe
        insurance_1989_2026[col] = [
            val if val != '' else np.nan for val in insurance_1989_2026[col].values
        ]

    for col in int_cols:
        insurance_1989_2026[col] = insurance_1989_2026[col].astype('Int64')

    for col in float_cols:
        insurance_1989_2026[col] = insurance_1989_2026[col].astype(float)

    print()
    print('Combining datasets.')
    df = pd.concat([insurance_1948_1988, insurance_1989_2026]).reset_index(drop=True)

    # the combined dataset should have the same number of rows as the sum of the two we are combining
    assert df.shape[0] == insurance_1948_1988.shape[0] + insurance_1989_2026.shape[0]

    # and the same number of columns as the 1989-2026 data
    assert df.shape[1] == insurance_1989_2026.shape[1]

    # let's clean up the `commodity_name` column
    df['commodity_name'] = df.commodity_name.str.lower()

    # the fips codes should actually be a combination of the `state_code` and `fips` columns
    df['fips'] = df['state_code'] + df['fips']
    df.drop('state_code', axis=1, inplace=True)

    # save combined dataset locally
    print()
    print('Saving data.')
    if start_year == end_year:
        df.to_parquet(f'{OUTPUT_DIR}/usda_crop_insurance_{start_year}.parquet')
    else:
        df.to_parquet(f'{OUTPUT_DIR}/usda_crop_insurance_{start_year}_{end_year}.parquet')

    print()
    print(f'Finished! The consolidated crop insurance is now saved in: {OUTPUT_DIR.resolve()}')
    print()


if __name__ == '__main__':
    try:
        process_crop_insurance_data()
    except KeyboardInterrupt:
        print()
        sys.exit('Interrupted by user.')
