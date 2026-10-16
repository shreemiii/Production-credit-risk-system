
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, accuracy_score

df = pd.read_csv("sample/application_train.csv")

X = df.drop(columns=["TARGET", "SK_ID_CURR"])
X = X.select_dtypes(include="number")
y = df["TARGET"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = make_pipeline(
    SimpleImputer(strategy="median"),
    StandardScaler(),
    LogisticRegression(max_iter=1000)
)

model.fit(X_train, y_train)

probabilities = model.predict_proba(X_test)[:, 1]
predictions = model.predict(X_test)

print("ROC-AUC:", round(roc_auc_score(y_test, probabilities), 4))
print("Accuracy:", round(accuracy_score(y_test, predictions), 4))
