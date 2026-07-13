"""
Gold layer fact table builders.

This module contains transformation functions responsible for building
the fact tables used by the Gold layer star schema.
"""

import pandas as pd


FACT_COLUMNS = [
    "monthly_inhand_salary",
    "num_bank_accounts",
    "num_credit_card",
    "interest_rate",
    "num_of_loan",
    "delay_from_due_date",
    "num_of_delayed_payment",
    "changed_credit_limit",
    "num_credit_inquiries",
    "credit_mix",
    "outstanding_debt",
    "credit_utilization_ratio",
    "credit_history_age",
    "payment_of_min_amount",
    "total_emi_per_month",
    "amount_invested_monthly",
    "payment_behaviour",
    "monthly_balance",
]


def build_credit_profile_fact(
    dataframe: pd.DataFrame,
    customer_dimension: pd.DataFrame,
    occupation_dimension: pd.DataFrame,
    credit_score_dimension: pd.DataFrame,
    date_dimension: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build the Gold fact table.

    Args:
        dataframe:
            Silver dataframe.

        customer_dimension:
            Customer dimension.

        occupation_dimension:
            Occupation dimension.

        credit_score_dimension:
            Credit score dimension.

        date_dimension:
            Date dimension.

    Returns:
        Fact table dataframe.
    """

    fact = dataframe.copy()

    fact = fact.merge(
        customer_dimension[
            [
                "customer_key",
                "customer_id",
            ]
        ],
        on="customer_id",
        how="left",
    )

    fact = fact.merge(
        occupation_dimension,
        on="occupation",
        how="left",
    )

    fact = fact.merge(
        credit_score_dimension[
            [
                "credit_score_key",
                "credit_score",
            ]
        ],
        on="credit_score",
        how="left",
    )

    fact = fact.merge(
        date_dimension[
            [
                "date_key",
                "month_name",
            ]
        ],
        left_on="month",
        right_on="month_name",
        how="left",
    )

    fact = fact.drop(
        columns=[
            "customer_id",
            "occupation",
            "credit_score",
            "month",
            "month_name",
        ]
    )

    fact = fact[
        [
            "customer_key",
            "occupation_key",
            "credit_score_key",
            "date_key",
            *FACT_COLUMNS,
        ]
    ]

    return fact