"""Summary of sampled applicant and credit-history tables."""
import json
from src.data import load_table
from src.utils import memory_mb,reduce_memory
SUMMARY_FILENAME="table_summary.json"
SUMMARY_KEYS=("table","rows","cols","mb_before","mb_after","missing_pct")

def summarize_table(df,name):
    rows,cols=df.shape
    return {"table":name,"rows":int(rows),"cols":int(cols),
            "mb_before":float(memory_mb(df)),"mb_after":float(memory_mb(reduce_memory(df))),
            "missing_pct":float(df.isna().sum().sum()*100/(rows*cols)) if rows*cols else 0.0}

def summarize_all(config):
    rows=[summarize_table(load_table(name,config),name) for name in config["tables"]]
    path=config["paths"]["reports_dir"]/SUMMARY_FILENAME
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(rows,indent=2)+"\n")
    return rows
