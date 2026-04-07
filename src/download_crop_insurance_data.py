import argparse
import io
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


def scrape_crop_insurance_data():
    """
    This script downloads crop insurance data from the USDA's Risk Management Agency site:
    https://www.rma.usda.gov/tools-reports/summary-of-business/state-county-crop-summary-business

    The data is split into two parts, one from 1948 - 1988 and the other from 1989 - present.
    They are formatted slightly differently, with the earlier time period's data being a consolidated
    text file, whereas data after 1988 is in individual text files.
    """

    def valid_year(year: str) -> None:
        """
        Assert that input argument `year` is of type int and is in the range [1995, 2026].
        """
        try:
            year = int(year)
        except ValueError:
            raise argparse.ArgumentTypeError('Year values must be of type `int`.')

        valid_years = list(range(1995, 2027, 1))
        if year not in valid_years:
            raise argparse.ArgumentTypeError(
                f'Year values must be between [{valid_years[0]}, {valid_years[-1]}].'
            )

        return year

    parser = argparse.ArgumentParser(
        description='Web scraping script for USDA RMA crop insurance statistics.'
    )

    parser.add_argument(
        '-sy',
        '--start-year',
        type=valid_year,
        default=1988,
        help='Year to begin web scraping. Min supported year is `1988`.',
    )

    parser.add_argument(
        '-ey',
        '--end-year',
        type=valid_year,
        default=datetime.today().year,
        help='Year to end web scraping. Max supported year is `2026`.',
    )

    args = parser.parse_args()
    START_YEAR = args.start_year
    END_YEAR = args.end_year

    # check to make sure end year >= start year
    if END_YEAR < START_YEAR:
        raise ValueError('Please enter an end year >= to the start year.')

    SCRIPT_DIR = Path(__file__).resolve().parent  # ./src
    PROJECT_ROOT = SCRIPT_DIR.resolve().parent  # .. project root
    OUTPUT_DIR = PROJECT_ROOT / 'data' / 'raw'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # https://www.rma.usda.gov/tools-reports/summary-of-business/state-county-crop-summary-business
    BASE_URL = (
        'https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/state_county_crop'
    )

    print()
    years_list = [
        str(date.year)
        for date in pd.date_range(start=f'{START_YEAR}-01-01', end=f'{END_YEAR}-01-01', freq='YS')
    ]
    for year in tqdm(years_list, position=0, leave=True):
        tqdm.write(f'Downloading data for year: {year}')

        if year == '1988':
            prefix = 'sobscc'
            download_url = f'{BASE_URL}/{prefix}_1948_1988.zip'
            in_filename = f'{prefix}48-88.txt'
            out_filename = 'sobcov_1948_1988.txt'
        else:
            prefix = 'sobcov'
            download_url = f'{BASE_URL}/{prefix}_{year}.zip'

            # input text file naming convention changes in 2016
            if int(year) < 2016:
                in_filename = f'{prefix}{year[-2:]}.txt'
            else:
                in_filename = f'{prefix}_{year}.txt'
            out_filename = f'{prefix}_{year}.txt'

        # https://stackoverflow.com/a/16511493
        # handle errors with try / except for requests package
        try:
            response = requests.get(download_url)
            response.raise_for_status()

            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            # save the text file directly from the ZIP without extracting
            with zip_file.open(in_filename) as file:
                # decode bytes to string
                # text_content = f.read().decode('utf-8')
                with open(f'{OUTPUT_DIR}/{out_filename}', 'wb') as f:
                    f.write(file.read())

        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)
        except requests.exceptions.ConnectionError as err:
            raise SystemExit(err)
        except requests.exceptions.Timeout as err:
            raise SystemExit(err)
        except requests.exceptions.RequestException as err:
            raise SystemExit(err)

    print()
    print(f'Finished! All extracted crop insurance files are in: {OUTPUT_DIR.resolve()}')
    print()


if __name__ == '__main__':
    try:
        scrape_crop_insurance_data()
    except KeyboardInterrupt:
        print()
        sys.exit('Interrupted by user.')
