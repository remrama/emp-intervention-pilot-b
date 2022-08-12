import os
import csv
import json

import numpy as np
import pandas as pd
from scipy import stats

import utils

export_dir = os.path.join(utils.load_config().bids_root,
    "derivatives", "pandas")
export_basename = "task-eat_agg-sub_corrs.tsv"
export_filepath = os.path.join(export_dir, export_basename)
utils.make_pathdir_if_not_exists(export_filepath)

import_dir = os.path.join(utils.load_config().bids_root, "derivatives", "pandas")
import_path1 = os.path.join(import_dir, "task-eat_acq-pre_agg-sub_corrs.tsv")
import_path2 = os.path.join(import_dir, "task-eat_acq-post_agg-sub_corrs.tsv")

df1 = pd.read_csv(import_path1, sep="\t")
df2 = pd.read_csv(import_path2, sep="\t")
df1.insert(1, "acquisition_id", "pre")
df2.insert(1, "acquisition_id", "post")

df = pd.concat([df1, df2])

df = df.sort_values(["participant_id", "acquisition_id"], ascending=[True, False])

intervention = df["participant_id"].apply(lambda x: "svp" if int(x.split("-")[1])%2 == 0 else "bct")
df.insert(1, "intervention", intervention.tolist())


df.to_csv(export_filepath, sep="\t", index=False)