import os
import json
from itertools import repeat
import pandas as pd

import utils

global_metadata = utils.load_config(as_object=False)["global_bids_metadata"]
practice_video_id = utils.load_config().practice_video_id
sample_rate_hz = utils.load_config().eat_sample_rate_hz
sample_rate_s = 1/sample_rate_hz

task_metadata = {
    "TaskName": "Empathy Accuracy Task",
    "TaskDescription": "A behavioral measure of empathy. See Ong et al., 2019 for details (https://doi.org/10.1109/TAFFC.2019.2955949 and https://github.com/desmond-ong/TAC-EA-model)",
    "Instructions": [
        "As you watch the following videos, continuously rate how positive or negative you believe the speaker is feeling at every moment."
    ]
}

column_metadata = {
    "trial_number": {
        "LongName": "Trial number",
        "Description": "Trial number"
    },
    "stimulus": {
        "LongName": "Video stimulus",
        "Description": "Video ID (in reference to SENDv1 dataset)"
    },
    "time": {
        "LongName": "Time of sample",
        "Description": "Responses were made continuously, but here resampled to 2 Hz",
        "Units": "seconds",
    },
    "response": {
        "LongName": "Response at current sample",
        "Description": "The slider position at the given sample time"
    }
}

column_names = list(column_metadata.keys())

sidecar = task_metadata | global_metadata | column_metadata

file_list = utils.find_source_files("eat", "json")


# path_basename = "target_112_3_normal.csv"
for file in file_list:
    with open(file, "r", encoding="utf-8") as f:
        subject_data = json.load(f)
    # remove practice trial
    subject_data = { k: v for k, v in subject_data.items() if k != practice_video_id }
    # wrangle
    trials = [ [repeat(i+1, len(v)), repeat(k, len(v)),
                [ sample_rate_s*j for j in range(len(v)) ], v]
        for i, (k, v) in enumerate(subject_data.items()) ]
    df = pd.concat([ pd.DataFrame(t).T for t in trials ])
    sub, ses, task = utils.filename2labels(file)
    basename = os.path.basename(file).replace(".json", "_beh.tsv").replace("_ses-001", ""
        ).replace("-eatA", "-eat_acq-pre").replace("-eatB", "-eat_acq-post")
    data_filepath = os.path.join(utils.load_config().bids_root, sub, "beh", basename)
    utils.make_pathdir_if_not_exists(data_filepath)
    df.to_csv(data_filepath, header=column_names, index=False, sep="\t", float_format="%.0f")
    utils.pretty_sidecar_export(sidecar, data_filepath)