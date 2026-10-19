
"""Join per-applicant feature tables onto the application table."""

from __future__ import annotations

import pandas as pd

COUNT_SUFFIX = "_COUNT"


def assert_one_row_per_applicant(
    df: pd.DataFrame, expected_ids: pd.Series, id_col: str = "SK_ID_CURR"
) -> None:
    expected = pd.Index(expected_ids)

    if id_col not in df.columns:
        raise ValueError(f"Missing applicant ID column: {id_col}")

    if len(df) != len(expected):
        raise ValueError(
            f"{len(df):,} rows for {len(expected):,} applicants"
        )

    if df[id_col].duplicated().any():
        count = int(df[id_col].duplicated().sum())
        raise ValueError(f"{count} duplicate applicant IDs found")

    if set(df[id_col]) != set(expected):
        missing = set(expected) - set(df[id_col])
        extra = set(df[id_col]) - set(expected)

        raise ValueError(
            f"Applicant IDs do not match: "
            f"{len(missing)} missing, {len(extra)} unexpected"
        )


def join_features(
    app: pd.DataFrame,
    feature_tables: dict[str, pd.DataFrame],
    id_col: str = "SK_ID_CURR",
) -> pd.DataFrame:

    result = app.copy()
    expected_ids = app[id_col]

    assert_one_row_per_applicant(result, expected_ids, id_col)

    for name, table in feature_tables.items():

        if id_col not in table.columns:
            raise ValueError(f"{name}: missing {id_col}")

        if table[id_col].duplicated().any():
            raise ValueError(
                f"{name}: duplicate applicant IDs; "
                "aggregate the table before joining"
            )

        new_columns = [
            col for col in table.columns if col != id_col
        ]

        duplicates = set(new_columns) & set(result.columns)

        if duplicates:
            raise ValueError(
                f"{name}: feature columns already exist: "
                f"{sorted(duplicates)}"
            )

        result = result.merge(
            table,
            on=id_col,
            how="left",
            sort=False,
            validate="one_to_one",
        )

        for col in new_columns:
            if col.endswith(COUNT_SUFFIX):
                result[col] = result[col].fillna(0)

        assert_one_row_per_applicant(
            result, expected_ids, id_col
        )

    return result
