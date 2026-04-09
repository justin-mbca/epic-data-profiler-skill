import pandas as pd
import numpy as np
import logging
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO)


def profile_epic_data(file_path: str, columns_to_profile: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Profiles an Epic EHR data export (CSV, JSON, or Parquet) and returns summary statistics and data quality warnings.

    Args:
        file_path (str): Path to the Epic data export (CSV, JSON, or Parquet).
        columns_to_profile (Optional[List[str]]): Subset of columns to profile (default: all).

    Returns:
        Dict[str, Any]: {
            'summary': {column: stats, ...},
            'errors': [str, ...]
        }
    """
    summary = {}
    errors = []
    warnings = []

    # Load data
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)
        else:
            errors.append(f"Unsupported file type: {file_path}")
            return {'summary': {}, 'errors': errors}
    except Exception as e:
        errors.append(f"Failed to load file: {str(e)}")
        return {'summary': {}, 'errors': errors}

    # Select columns
    if columns_to_profile:
        missing_cols = [col for col in columns_to_profile if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        cols = [col for col in columns_to_profile if col in df.columns]
    else:
        cols = df.columns.tolist()

    # Profile columns
    for col in cols:
        col_data = df[col]
        col_summary = {}
        col_summary['type'] = str(col_data.dtype)
        col_summary['unique'] = int(col_data.nunique(dropna=True))
        col_summary['missing'] = int(col_data.isna().sum())
        col_summary['sample'] = col_data.dropna().astype(str).unique().tolist()[:3]

        if np.issubdtype(col_data.dtype, np.number):
            col_summary['min'] = float(np.nanmin(col_data)) if not col_data.isna().all() else None
            col_summary['max'] = float(np.nanmax(col_data)) if not col_data.isna().all() else None
            col_summary['mean'] = float(np.nanmean(col_data)) if not col_data.isna().all() else None
            # Outlier detection (simple)
            if col_summary['unique'] > 0 and not col_data.isna().all():
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                outliers = col_data[(col_data < q1 - 1.5 * iqr) | (col_data > q3 + 1.5 * iqr)]
                if len(outliers) > 0:
                    col_summary.setdefault('warnings', []).append('Possible outliers detected')
        else:
            # Check for possible mixed types
            if col_data.apply(lambda x: isinstance(x, (int, float)) or pd.isna(x)).sum() < len(col_data) * 0.8:
                col_summary.setdefault('warnings', []).append('Non-numeric values in mostly numeric column')

        summary[col] = col_summary

    return {'summary': summary, 'errors': errors}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Profile Epic EHR data export.")
    parser.add_argument('--file_path', type=str, required=True, help='Path to CSV or JSON Epic export')
    parser.add_argument('--columns', type=str, nargs='*', help='Columns to profile (optional)')
    args = parser.parse_args()
    result = profile_epic_data(args.file_path, args.columns)
    print(result)
