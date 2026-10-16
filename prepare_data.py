
import pandas as pd
from pathlib import Path

df = pd.read_csv("application_train.csv")

sample = df.sample(n=5000, random_state=42)
sample = sample.sort_values("SK_ID_CURR")

Path("sample").mkdir(exist_ok=True)
sample.to_csv("sample/application_train.csv", index=False)

print("Total applicants:", len(sample))
print("Unique applicants:", sample["SK_ID_CURR"].nunique())
print("Total features:", len(sample.columns))
print("Default rate:", round(sample["TARGET"].mean() * 100, 2), "%")
