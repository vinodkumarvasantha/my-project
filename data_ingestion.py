"""
Data Ingestion
Loads all 10 raw CSV datasets, inspects them, validates AMFI codes,
and writes a data quality summary to reports/.
"""

import pandas as pd
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

RAW_DATA_DIR = 'data/raw'
REPORTS_DIR = 'reports'

FILES = [
    '01_fund_master.csv',
    '02_nav_history.csv',
    '03_aum_by_fund_house.csv',
    '04_monthly_sip_inflows.csv',
    '05_category_inflows.csv',
    '06_industry_folio_count.csv',
    '07_scheme_performance.csv',
    '08_investor_transactions.csv',
    '09_portfolio_holdings.csv',
    '10_benchmark_indices.csv',
]


def load_all_datasets():
    """Load all CSVs into a dict of DataFrames, keyed by filename."""
    dfs = {}
    for f in FILES:
        path = os.path.join(RAW_DATA_DIR, f)
        df = pd.read_csv(path)
        dfs[f] = df
    return dfs


def inspect_datasets(dfs):
    """Print shape, dtypes, and head for each dataset. Flag basic anomalies."""
    for f, df in dfs.items():
        print("=" * 100)
        print(f"FILE: {f}")
        print("=" * 100)
        print(f"\nSHAPE: {df.shape}")
        print(f"\nDTYPES:\n{df.dtypes}")
        print(f"\nHEAD:\n{df.head()}")

        nulls = df.isnull().sum()
        nulls = nulls[nulls > 0]
        print(f"\nNulls:\n{nulls if len(nulls) else 'None'}")
        print(f"Duplicate rows: {df.duplicated().sum()}")
        print()


def explore_fund_master(fund_master):
    """Print unique fund houses, categories, sub-categories, risk grades."""
    print("=" * 60)
    print("FUND MASTER EXPLORATION")
    print("=" * 60)

    print("\nUnique fund houses:", fund_master['fund_house'].unique())
    print("Total fund houses:", fund_master['fund_house'].nunique())

    print("\nUnique categories:", fund_master['category'].unique())
    print("\nUnique sub-categories:", fund_master['sub_category'].unique())

    if 'risk_grade' in fund_master.columns:
        print("\nUnique risk grades:", fund_master['risk_grade'].unique())

    print("\namfi_code is unique:", fund_master['amfi_code'].is_unique)
    print("amfi_code digit lengths:\n", fund_master['amfi_code'].astype(str).str.len().value_counts())


def validate_amfi_codes(fund_master, nav_history):
    """Confirm every fund_master code exists in nav_history. Return a summary string."""
    master_codes = set(fund_master['amfi_code'])
    nav_codes = set(nav_history['amfi_code'])

    missing_from_nav = master_codes - nav_codes
    missing_from_master = nav_codes - master_codes

    nav_counts = nav_history.groupby('amfi_code').size().reset_index(name='nav_record_count')
    nav_counts = nav_counts.merge(fund_master[['amfi_code', 'scheme_name']], on='amfi_code', how='left')

    total_funds = len(master_codes)
    matched_funds = len(master_codes & nav_codes)
    match_rate = (matched_funds / total_funds) * 100 if total_funds else 0

    summary = f"""
DATA QUALITY SUMMARY — AMFI Code Validation
=============================================
Total funds in fund_master:         {total_funds}
Funds with matching NAV history:    {matched_funds} ({match_rate:.1f}%)
Funds missing from nav_history:     {len(missing_from_nav)}
Orphan codes in nav_history:        {len(missing_from_master)}

NAV records per fund — min: {nav_counts['nav_record_count'].min()},
max: {nav_counts['nav_record_count'].max()},
mean: {nav_counts['nav_record_count'].mean():.0f}

Conclusion: {"All fund_master codes have corresponding NAV history — no gaps." if len(missing_from_nav) == 0 else f"{len(missing_from_nav)} funds have no NAV history and need investigation before analysis."}
"""
    print(summary)
    return summary


def main():
    print("Loading all datasets...\n")
    dfs = load_all_datasets()

    print("Inspecting datasets...\n")
    inspect_datasets(dfs)

    fund_master = dfs['01_fund_master.csv']
    nav_history = dfs['02_nav_history.csv']

    explore_fund_master(fund_master)

    summary = validate_amfi_codes(fund_master, nav_history)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    summary_path = os.path.join(REPORTS_DIR, 'data_quality_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"Data quality summary saved to {summary_path}")


if __name__ == '__main__':
    main()