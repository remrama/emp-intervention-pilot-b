import os
import numpy as np
import pandas as pd
from scipy import stats

import utils


export_dir = os.path.join(utils.load_config().bids_root,
    "derivatives", "pandas")
export_basename_data = "task-bct_agg-sub_rrate.tsv"
export_basename_descr = "task-bct_agg-sub_rrate_descr.tsv"
export_filepath_data = os.path.join(export_dir, export_basename_data)
export_filepath_descr = os.path.join(export_dir, export_basename_descr)
utils.make_pathdir_if_not_exists(export_filepath_descr)


df = utils.stack_raw_task_data("bct")

# def cycle_accuracy(row):
#     if row["response"] == reset_response:
#         return "selfcaught"
#     elif row["press"] < target:
#         return "undershoot"
#     elif row["press"] > target:
#         return "overshoot"
#     elif row["press"] == target:
#         return "correct"
#     else:
#         raise ValueError("Should never get here")
# cycle_df["cycle_accuracy"] = cycle_df.apply(cycle_accuracy, axis=1)


cycle_df = df.groupby(["participant_id","cycle"]
    ).agg({
        "response_time": ["mean", "std"],
        "press_accuracy": "last"
    })
cycle_df.columns = cycle_df.columns.map(lambda x: "-".join(x))
cycle_df = cycle_df.rename(columns={"press_accuracy-last": "cycle_accuracy"})
cycle_df["cycle_correct"] = cycle_df["cycle_accuracy"].eq("correct")

participant_df = cycle_df.groupby("participant_id").mean()
participant_df.columns = participant_df.columns.map(lambda x: x.replace("response", "cycle_response"))

participant_df.to_csv(export_filepath_data, index=True, float_format="%.2f", sep="\t")
participant_df.describe().to_csv(export_filepath_descr, index_label="statistic", float_format="%.2f", sep="\t")
