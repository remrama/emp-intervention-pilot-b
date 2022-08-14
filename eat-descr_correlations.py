import os
import csv
import json

import numpy as np
import pandas as pd
from scipy import stats

import utils



export_dir = os.path.join(utils.load_config().bids_root,
    "derivatives", "pandas")
export_basename_data = "task-eat_acq-REPLACE_agg-sub_corrs.tsv"
export_basename_descr = "task-eat_acq-REPLACE_agg-sub_corrs_descr.tsv"
export_filepath_data = os.path.join(export_dir, export_basename_data)
export_filepath_descr = os.path.join(export_dir, export_basename_descr)
utils.make_pathdir_if_not_exists(export_filepath_descr)

# Add another output that includes individual video scores
export_basename_trials = "task-eat_agg-trial_corrs.tsv"
export_filepath_trials = os.path.join(export_dir, export_basename_trials)


df = utils.stack_raw_task_data("eat")


def get_correlation(ratings1, ratings2):
    # trim to account for minor size differences
    shortest_length = min((map(len, [ratings1, ratings2])))
    ratings1 = ratings1[:shortest_length]
    ratings2 = ratings2[:shortest_length]
    ratings1_z = stats.zscore(ratings1, nan_policy="raise")
    ratings2_z = stats.zscore(ratings2, nan_policy="raise")
    r, _ = stats.spearmanr(ratings1_z, ratings2_z)
    rz = np.arctanh(r)
    return rz

def empathy_accuracy_scores(ser):
    participant_timecourse = ser.tolist()
    _, _, video_id = ser.name
    # grab true timecourses from SEND dataset
    actor_timecourse, crowd_timecourse = utils.get_true_timecourses(video_id)
    # correlate
    r_actor = get_correlation(actor_timecourse, participant_timecourse)
    r_crowd = get_correlation(crowd_timecourse, participant_timecourse)
    return (r_actor, r_crowd)


trial_df = df.reset_index(
    ).groupby(["participant_id", "acquisition_id", "stimulus"]
    )["response"].apply(empathy_accuracy_scores)

trial_df = trial_df.apply(pd.Series)
trial_df.columns = ["actor_correlation", "crowd_correlation"]

trial_df.to_csv(export_filepath_trials, index=True, float_format="%.3f", sep="\t")


# cycle_df = df.groupby(["participant_id","cycle"]
#     ).agg({
#         "response_time": ["mean", "std"],
#         "press_accuracy": "last"
#     })
# cycle_df.columns = cycle_df.columns.map(lambda x: "-".join(x))
# cycle_df = cycle_df.rename(columns={"press_accuracy-last": "cycle_accuracy"})
# cycle_df["cycle_correct"] = cycle_df["cycle_accuracy"].eq("correct")

for acquisition_id, acquisition_df in trial_df.groupby("acquisition_id"):
    participant_df = acquisition_df.groupby("participant_id").agg(["mean", "std", "min", "max"])
    participant_df.columns = participant_df.columns.map(lambda x: "-".join(x))
    export_path_data = export_filepath_data.replace("acq-REPLACE", acquisition_id)
    export_path_descr = export_filepath_descr.replace("acq-REPLACE", acquisition_id)
    participant_df.to_csv(export_path_data, index=True, float_format="%.3f", sep="\t")
    participant_df.describe().to_csv(export_path_descr, index_label="statistic", float_format="%.2f", sep="\t")