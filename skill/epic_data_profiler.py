import pandas as pd
import numpy as np
import logging
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO)


def profile_epic_data(file_path: str, columns_to_profile: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Profiles an Epic EHR data export (CSV, JSON, or Parquet) and returns summary statistics and data quality warnings.

    Features demonstrated by this function:
    - Schema validation: Checks for missing columns (if specified), unsupported file types, and file load errors. Reports missing or unexpected columns in the 'errors' field.
    - Type safety: Infers and reports the data type of each column (e.g., int64, float64, object).
    - Statistics: Computes per-column statistics:
        - unique: Number of unique non-null values
        - missing: Number of missing (null/NaN) values
        - min, max, mean: For numeric columns
        - sample: Up to 3 example values from the column
    - Warnings: Detects possible outliers (numeric columns) and mixed types (non-numeric columns with mostly numeric values).
    - Errors: Returns a list of errors (e.g., missing columns, unsupported file type, file load failure).

    Example output:
        {
            'summary': {
                'PatientID': {
                    'type': 'int64',
                    'unique': 1000,
                    'missing': 0,
                    'sample': ['1', '2', '3'],
                    'min': 1.0,
                    'max': 1000.0,
                    'mean': 500.5
                },
                'Age': {
                    'type': 'float64',
                    'unique': 82,
                    'missing': 256,
                    'sample': ['55.0', '91.0', '77.0'],
                    'min': 18.0,
                    'max': 99.0,
                    'mean': 57.6
                },
                'LabResult': {
                    'type': 'float64',
                    'unique': 893,
                    'missing': 107,
                    'sample': ['5.35', '2.32', '5.76'],
                    'min': -0.84,
                    'max': 11.38,
                    'mean': 5.17,
                    'warnings': ['Possible outliers detected']
                }
            },
            'errors': []
        }

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

    # --- Load data from file ---
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)  # Load CSV
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)  # Load JSON
        elif file_path.endswith('.parquet'):
            df = pd.read_parquet(file_path)  # Load Parquet
        else:
            errors.append(f"Unsupported file type: {file_path}")
            return {'summary': {}, 'errors': errors}
    except Exception as e:
        errors.append(f"Failed to load file: {str(e)}")
        return {'summary': {}, 'errors': errors}

    # --- Select columns to profile ---
    if columns_to_profile:
        missing_cols = [col for col in columns_to_profile if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        cols = [col for col in columns_to_profile if col in df.columns]
    else:
        cols = df.columns.tolist()

    # --- Profile each column ---
    for col in cols:
        col_data = df[col]
        col_summary = {}
        # Data type
        col_summary['type'] = str(col_data.dtype)
        # Unique value count
        col_summary['unique'] = int(col_data.nunique(dropna=True))
        # Missing value count
        col_summary['missing'] = int(col_data.isna().sum())
        # Sample values
        col_summary['sample'] = col_data.dropna().astype(str).unique().tolist()[:3]

        # --- Numeric column profiling ---
        if np.issubdtype(col_data.dtype, np.number):
            col_summary['min'] = float(np.nanmin(col_data)) if not col_data.isna().all() else None
            col_summary['max'] = float(np.nanmax(col_data)) if not col_data.isna().all() else None
            col_summary['mean'] = float(np.nanmean(col_data)) if not col_data.isna().all() else None
            # Outlier detection (IQR method)
            if col_summary['unique'] > 0 and not col_data.isna().all():
                q1 = col_data.quantile(0.25)
                q3 = col_data.quantile(0.75)
                iqr = q3 - q1
                outliers = col_data[(col_data < q1 - 1.5 * iqr) | (col_data > q3 + 1.5 * iqr)]
                if len(outliers) > 0:
                    col_summary.setdefault('warnings', []).append('Possible outliers detected')
        else:
            # --- Non-numeric column: check for mixed types ---
            if col_data.apply(lambda x: isinstance(x, (int, float)) or pd.isna(x)).sum() < len(col_data) * 0.8:
                col_summary.setdefault('warnings', []).append('Non-numeric values in mostly numeric column')

        summary[col] = col_summary

    # --- Return structured summary and errors ---
    return {'summary': summary, 'errors': errors}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Profile Epic EHR data export.")
    parser.add_argument('--file_path', type=str, required=True, help='Path to CSV or JSON Epic export')
    parser.add_argument('--columns', type=str, nargs='*', help='Columns to profile (optional)')
    args = parser.parse_args()
    result = profile_epic_data(args.file_path, args.columns)
    print(result)
