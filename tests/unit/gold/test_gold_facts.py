"""
Unit tests for Gold fact table.
"""

import pandas as pd

from src.processing.gold.dimensions import (
    build_credit_score_dimension,
    build_customer_dimension,
    build_date_dimension,
    build_occupation_dimension,
)
from src.processing.gold.facts import (
    build_credit_profile_fact,
)


def test_build_credit_profile_fact_returns_expected_columns():
    dataframe = pd.DataFrame(
        {
            "customer_id": ["C1"],
            "month": ["January"],
            "occupation": ["Engineer"],
            "credit_score": ["Good"],
            "age": [30],
            "annual_income": [50000.0],
            "monthly_inhand_salary": [4000.0],
            "num_bank_accounts": [2],
            "num_credit_card": [1],
            "interest_rate": [8.5],
            "num_of_loan": [1],
            "delay_from_due_date": [0],
            "num_of_delayed_payment": [0],
            "changed_credit_limit": [1000.0],
            "num_credit_inquiries": [2],
            "credit_mix": ["Good"],
            "outstanding_debt": [1500.0],
            "credit_utilization_ratio": [25.0],
            "credit_history_age": ["10 Years"],
            "payment_of_min_amount": ["Yes"],
            "total_emi_per_month": [300.0],
            "amount_invested_monthly": [500.0],
            "payment_behaviour": [
                "Low_spent_Small_value_payments"
            ],
            "monthly_balance": [2500.0],
        }
    )

    customer_dimension = build_customer_dimension(dataframe)

    occupation_dimension = build_occupation_dimension(dataframe)

    credit_score_dimension = (
        build_credit_score_dimension(dataframe)
    )

    date_dimension = build_date_dimension(dataframe)

    fact = build_credit_profile_fact(
        dataframe=dataframe,
        customer_dimension=customer_dimension,
        occupation_dimension=occupation_dimension,
        credit_score_dimension=credit_score_dimension,
        date_dimension=date_dimension,
    )

    assert len(fact) == 1

    assert "customer_key" in fact.columns
    assert "occupation_key" in fact.columns
    assert "credit_score_key" in fact.columns
    assert "date_key" in fact.columns

    assert "customer_id" not in fact.columns
    assert "occupation" not in fact.columns
    assert "credit_score" not in fact.columns
    assert "month" not in fact.columns


def test_build_credit_profile_fact_preserves_row_count():
    dataframe = pd.DataFrame(
        {
            "customer_id": ["C1", "C2"],
            "month": ["January", "February"],
            "occupation": ["Engineer", "Doctor"],
            "credit_score": ["Good", "Poor"],
            "age": [30, 40],
            "annual_income": [50000.0, 70000.0],
            "monthly_inhand_salary": [4000.0, 6000.0],
            "num_bank_accounts": [2, 3],
            "num_credit_card": [1, 2],
            "interest_rate": [8.5, 12.0],
            "num_of_loan": [1, 2],
            "delay_from_due_date": [0, 5],
            "num_of_delayed_payment": [0, 2],
            "changed_credit_limit": [1000.0, 2000.0],
            "num_credit_inquiries": [2, 4],
            "credit_mix": ["Good", "Bad"],
            "outstanding_debt": [1500.0, 5000.0],
            "credit_utilization_ratio": [25.0, 70.0],
            "credit_history_age": [
                "10 Years",
                "20 Years",
            ],
            "payment_of_min_amount": [
                "Yes",
                "No",
            ],
            "total_emi_per_month": [300.0, 800.0],
            "amount_invested_monthly": [
                500.0,
                200.0,
            ],
            "payment_behaviour": [
                "Low_spent_Small_value_payments",
                "High_spent_Large_value_payments",
            ],
            "monthly_balance": [
                2500.0,
                1800.0,
            ],
        }
    )

    fact = build_credit_profile_fact(
        dataframe=dataframe,
        customer_dimension=build_customer_dimension(
            dataframe
        ),
        occupation_dimension=build_occupation_dimension(
            dataframe
        ),
        credit_score_dimension=build_credit_score_dimension(
            dataframe
        ),
        date_dimension=build_date_dimension(
            dataframe
        ),
    )

    assert len(fact) == len(dataframe)