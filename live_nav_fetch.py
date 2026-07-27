"""
Day 1: Live NAV Fetch
Fetches live NAV history from mfapi.in for key schemes and saves as raw CSV.
"""

import requests
import pandas as pd
import time
import os

RAW_DATA_DIR = 'data/raw'

# Key schemes to fetch
SCHEMES = {
    "125497": "HDFC Top 100 Direct",
    "119551": "SBI Bluechip",
    "120503": "ICICI Bluechip",
    "118632": "Nippon Large Cap",
    "119092": "Axis Bluechip",
    "120841": "Kotak Bluechip",
}


def fetch_scheme_nav(scheme_code):
    """Fetch NAV history for a single scheme code from mfapi.in."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data['data'])
    df['scheme_code'] = data['meta']['scheme_code']
    df['scheme_name'] = data['meta']['scheme_name']
    df['fund_house'] = data['meta']['fund_house']
    return df


def fetch_all_schemes(schemes):
    """Fetch NAV history for multiple schemes, return combined DataFrame."""
    all_dfs = []
    for code, name in schemes.items():
        print(f"Fetching {name} ({code})...")
        df = fetch_scheme_nav(code)
        all_dfs.append(df)
        print(f"  -> {df.shape[0]} NAV records fetched")
        time.sleep(1)  # be polite to the API

    combined_df = pd.concat(all_dfs, ignore_index=True)
    return combined_df


def main():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    print("Fetching live NAV data for key schemes...\n")
    combined_df = fetch_all_schemes(SCHEMES)

    print(f"\nTotal records fetched: {combined_df.shape[0]}")
    print(combined_df['scheme_name'].value_counts())

    output_path = os.path.join(RAW_DATA_DIR, 'key_schemes_nav_live.csv')
    combined_df.to_csv(output_path, index=False)
    print(f"\nSaved to {output_path}")


if __name__ == '__main__':
    main()