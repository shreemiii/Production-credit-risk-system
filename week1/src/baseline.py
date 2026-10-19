"""Reproducible logistic regression baseline on the instructor's fixed split."""
import json
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from src.data import load_split
from src.metrics import evaluate
DAYS_EMPLOYED_SENTINEL = 365243
MODEL_NAME = "logistic_regression"
METRICS_KEYS = ("model","roc_auc","pr_auc","ks","n_train","n_valid","valid_default_rate","seed")

def clean_application(df):
    result = df.copy()
    flag = result["DAYS_EMPLOYED"] == DAYS_EMPLOYED_SENTINEL
    result["DAYS_EMPLOYED_ANOM"] = flag.astype(int)
    result.loc[flag, "DAYS_EMPLOYED"] = float("nan")
    return result

def get_feature_columns(df, config):
    ignore = {config["id_col"],config["target_col"]}
    nums = [c for c in df if c not in ignore and pd.api.types.is_numeric_dtype(df[c])]
    cats = [c for c in df if c not in ignore and c not in nums]
    return nums,cats

def build_preprocessor(numeric_cols,categorical_cols):
    nums = Pipeline([("imputer",SimpleImputer(strategy="median")),("scaler",StandardScaler())])
    cats = Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("encoder",OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("numeric",nums,numeric_cols),("categorical",cats,categorical_cols)])

def build_model(config,preprocessor):
    return Pipeline([("preprocessor",preprocessor),("model",LogisticRegression(max_iter=config["baseline"]["max_iter"],class_weight=config["baseline"]["class_weight"],random_state=config["seed"]))])

def write_metrics(metrics,extra,path):
    combined = {**metrics,**extra}
    if any(k not in combined for k in METRICS_KEYS):
        raise ValueError("Missing metric keys")
    combined = {k: v.item() if hasattr(v,"item") else v for k,v in combined.items()}
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(combined,indent=2)+"\n")

def run_baseline(config):
    import numpy as np
    np.random.seed(config["seed"])
    train,valid = load_split(config)
    train,valid = clean_application(train),clean_application(valid)
    nums,cats = get_feature_columns(train,config)
    columns=nums+cats
    model=build_model(config,build_preprocessor(nums,cats))
    model.fit(train[columns],train[config["target_col"]])
    scores=evaluate(valid[config["target_col"]],model.predict_proba(valid[columns])[:,1])
    extra={"model":MODEL_NAME,"n_train":len(train),"n_valid":len(valid),"valid_default_rate":float(valid[config["target_col"]].mean()),"seed":config["seed"]}
    write_metrics(scores,extra,config["paths"]["metrics_file"])
    return {**scores,**extra}
