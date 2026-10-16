"""Loading applicant tables and the fixed training/validation split."""
from __future__ import annotations

import pandas as pd


def load_table(name, config):
    if name not in config["tables"]:
        raise KeyError(f"Unknown table: {name}")
    path = config["paths"]["sample_dir"] / config["tables"][name]
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run python run.py sample first.")
    return pd.read_csv(path)


def load_application(config):
    return load_table("application_train", config)


def load_split(config):
    app = load_application(config)
    id_col = config["id_col"]
    split = pd.read_csv(config["paths"]["split_file"], dtype={id_col: app[id_col].dtype})
    if (split[id_col].duplicated().any() or app[id_col].duplicated().any()
            or set(split["split"]) != {"train", "valid"}
            or len(split) != len(app)
            or set(split[id_col]) != set(app[id_col])):
        raise ValueError("Fixed split must match applicants one-to-one with valid labels.")
    labels = split.set_index(id_col)["split"]
    assigned = app[id_col].map(labels)
    return (app.loc[assigned == "train"].reset_index(drop=True),
            app.loc[assigned == "valid"].reset_index(drop=True))
