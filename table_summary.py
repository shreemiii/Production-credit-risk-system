
import pandas as pd
from pathlib import Path

files = [
    "application_train.csv",
    "bureau.csv",
    "bureau_balance.csv",
    "previous_application.csv",
    "POS_CASH_balance.csv",
    "credit_card_balance.csv",
    "installments_payments.csv"
]

summary = []

for file in files:
    columns = pd.read_csv(file, nrows=0).columns

    with open(file, "rb") as f:
        lines = sum(
            block.count(b"\n")
            for block in iter(lambda: f.read(1024 * 1024), b"")
        )

    summary.append({
        "Table": file,
        "Rows": lines - 1,
        "Columns": len(columns),
        "ID Columns": ", ".join(
            c for c in columns if c.startswith("SK_ID")
        )
    })

result = pd.DataFrame(summary)
Path("reports").mkdir(exist_ok=True)
result.to_csv("reports/table_summary.csv", index=False)

print(result.to_string(index=False))
