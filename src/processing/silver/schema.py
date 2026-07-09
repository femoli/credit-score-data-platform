"""
Silver layer schema.

Defines the data contract for the Silver layer, including column names,
data types, validation rules, sensitivity classification, and business
descriptions.

Architecture notes:
The Silver schema acts as the single source of truth for cleaning,
typing, validation, documentation, and future data quality checks.
"""

# =============================================================================
# Constants
# =============================================================================

COLUMN_RENAME_MAPPING = {
    "ID": "record_id",
    "Customer_ID": "customer_id",
    "Month": "month",
    "Name": "name",
    "Age": "age",
    "SSN": "ssn",
    "Occupation": "occupation",
    "Annual_Income": "annual_income",
    "Monthly_Inhand_Salary": "monthly_inhand_salary",
    "Num_Bank_Accounts": "num_bank_accounts",
    "Num_Credit_Card": "num_credit_card",
    "Interest_Rate": "interest_rate",
    "Num_of_Loan": "num_of_loan",
    "Type_of_Loan": "type_of_loan",
    "Delay_from_due_date": "delay_from_due_date",
    "Num_of_Delayed_Payment": "num_of_delayed_payment",
    "Changed_Credit_Limit": "changed_credit_limit",
    "Num_Credit_Inquiries": "num_credit_inquiries",
    "Credit_Mix": "credit_mix",
    "Outstanding_Debt": "outstanding_debt",
    "Credit_Utilization_Ratio": "credit_utilization_ratio",
    "Credit_History_Age": "credit_history_age",
    "Payment_of_Min_Amount": "payment_of_min_amount",
    "Total_EMI_per_month": "total_emi_per_month",
    "Amount_invested_monthly": "amount_invested_monthly",
    "Payment_Behaviour": "payment_behaviour",
    "Monthly_Balance": "monthly_balance",
    "Credit_Score": "credit_score",
}

PII_COLUMNS = [
    "name",
    "ssn",
]

SILVER_SCHEMA = {
    "record_id": {"type": "string", "nullable": False},
    "customer_id": {"type": "string", "nullable": False},
    "month": {
        "type": "category",
        "nullable": False,
        "allowed_values": [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
             "December",
        ],
    },
    "age": {"type": "Int64", "nullable": True, "min": 0, "max": 120},
    "occupation": {"type": "category", "nullable": True},
    "annual_income": {"type": "Float64", "nullable": False, "min": 0},
    "monthly_inhand_salary": {"type": "Float64", "nullable": True, "min": 0},
    "num_bank_accounts": {"type": "Int64", "nullable": True, "min": 0},
    "num_credit_card": {"type": "Int64", "nullable": True, "min": 0},
    "interest_rate": {"type": "Float64", "nullable": True, "min": 0},
    "num_of_loan": {"type": "Int64", "nullable": True, "min": 0},
    "type_of_loan": {"type": "string", "nullable": True},
    "delay_from_due_date": {"type": "Int64", "nullable": True},
    "num_of_delayed_payment": {"type": "Int64", "nullable": True, "min": 0},
    "changed_credit_limit": {"type": "Float64", "nullable": True},
    "num_credit_inquiries": {"type": "Int64", "nullable": True, "min": 0},
    "credit_mix": {
        "type": "category",
        "nullable": True,
        "allowed_values": ["Good", "Standard", "Bad"],
    },
    "outstanding_debt": {"type": "Float64", "nullable": True, "min": 0},
    "credit_utilization_ratio": {"type": "Float64", "nullable": False, "min": 0},
    "credit_history_age": {"type": "string", "nullable": True},
    "payment_of_min_amount": {
        "type": "category",
        "nullable": True,
        "allowed_values": ["Yes", "No", "NM"],
    },
    "total_emi_per_month": {"type": "Float64", "nullable": True, "min": 0},
    "amount_invested_monthly": {"type": "Float64", "nullable": True, "min": 0},
    "payment_behaviour": {"type": "category", "nullable": True},
    "monthly_balance": {"type": "Float64", "nullable": True},
    "credit_score": {
        "type": "category",
        "nullable": False,
        "allowed_values": ["Good", "Standard", "Poor"],
    },
}

INTEGER_COLUMNS = [
    column
    for column, rules in SILVER_SCHEMA.items()
    if rules["type"] == "Int64"
]

FLOAT_COLUMNS = [
    column
    for column, rules in SILVER_SCHEMA.items()
    if rules["type"] == "Float64"
]

CATEGORICAL_COLUMNS = [
    column
    for column, rules in SILVER_SCHEMA.items()
    if rules["type"] == "category"
]

EXPECTED_COLUMNS = list(SILVER_SCHEMA.keys())

OPTIONAL_COLUMNS = [
    "credit_score",
]

REQUIRED_COLUMNS = [
    column
    for column in EXPECTED_COLUMNS
    if column not in OPTIONAL_COLUMNS
]