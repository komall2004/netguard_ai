import pandas as pd
import numpy as np


def recommend_missing_value(df, col):

    missing_percentage = df[col].isnull().mean() * 100

    if missing_percentage > 40:
        return "Drop Columns"

    if pd.api.types.is_numeric_dtype(df[col]):

        q1, q3 = np.percentile(
            df[col].dropna(),
            [25, 75]
        )

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = (
            (df[col] < lower) |
            (df[col] > upper)
        ).sum()

        if outliers > 0:
            return "Median"

        return "Mean"

    return "Mode"


def analyze_preprocessing(df):

    recommendations = {}

    # -------------------------
    # Missing values
    # -------------------------

    missing = df.isnull().sum()

    for col, count in missing.items():

        if count == 0:
            continue

        percentage = (count / len(df)) * 100

        recommendations[col] = {
            "missing_count": int(count),
            "missing_percentage": round(
                percentage,
                2
            ),
            "recommendation": recommend_missing_value(
                df,
                col
            )
        }

    # -------------------------
    # Categorical columns
    # -------------------------

    categorical = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    categorical = [
        col for col in categorical
        if col not in ["label", "difficulty"]
    ]

    # -------------------------
    # Numerical columns
    # -------------------------

    numerical = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    # -------------------------
    # Duplicate rows
    # -------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )

    # -------------------------
    # Scaling recommendation
    # -------------------------

    outliers_detected = False

    for col in numerical:

        if df[col].dropna().empty:
            continue

        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = (
            (df[col] < lower) |
            (df[col] > upper)
        ).sum()

        if outliers > 0:
            outliers_detected = True
            break

    if outliers_detected:
        scaling_recommendation = {
            "method": "RobustScaler",
            "reason": "Outliers were detected in numerical features."
        }
    else:
        scaling_recommendation = {
            "method": "StandardScaler",
            "reason": "No significant outliers were detected."
        }

    # -------------------------
    # Final result
    # -------------------------

    return {
        "missing_value_recommendations": recommendations,

        "categorical_columns": categorical,

        "categorical_encoding_recommendation": {
            "method": "One Hot Encoding",
            "reason": (
                "Detected categorical columns appear "
                "to be nominal."
            )
        },

        "numerical_columns": numerical,

        "scaling_recommendation": scaling_recommendation,

        "duplicate_rows": duplicate_count,

        "duplicate_recommendation": (
            "Review and consider removing duplicates"
            if duplicate_count > 0
            else "No duplicate rows detected"
        )
    }