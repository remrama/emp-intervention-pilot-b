"""Clean the BCT task data.
Go from raw json psychopy output to usable dataframe in BIDS format.
"""
import os
import json
import pandas as pd

import utils

global_metadata = utils.load_config(as_object=False)["global_bids_metadata"]

task_metadata = {
    "TaskName": "Breath Counting Task",
    "TaskDescription": "A behavioral meditation task. See Levinson et al., 2014 and Wong et al., 2018.",
    "Instructions": [
        "In the next task, we would like you to be aware of your breath. Focus on the movement of your breath in and out while breathing at a slow, comfortable pace.",
        "At some point, you may notice your attention has wandered from the breath. That's okay. Just gently place it back on the breath.",
        "To help attention stay with the breath, use part of your attention to silently count breaths from 1 to 9 again and again.",
        "Say the count softly in your mind (not out loud or with fingers) while most of the attention is on feeling the breath.",
        "During counting, press a button with each breath. Press either of the Top buttons on breaths 1-8 and the Trigger button on breath 9. If you find that you have forgotten the count, just press down on the Scroll Wheel and restart the count at 1 with the next breath.",
        "Sit in an upright, relaxed posture that feels comfortable.",
    ]
}

column_metadata = {

    "cycle": {
        "LongName": "Cycle count",
        "Description": "Indicates the cycle number, which ends on either a target or reset press."
    },

    "press": {
        "LongName": "Press count",
        "Description": "Indicates the press count within each cycle",
        "Levels": {
            "nontarget": "Breaths 1-8",
            "target": "Breath 9"
        }
    },

    "response": {
        "LongName": "Button response",
        "Description": "Indicator of what button was pushed",
        "Levels": {
            "left": "participant estimated a nontarget trial",
            "right": "participant estimated a target trial",
            "space": "participant lost count and reset counter"
        }
    },

    "response_time": {
        "Description": "Indicator of time between prior and current response",
        "Units": "milliseconds"
    },

    "press_accuracy": {
        "LongName": "Press accuracy",
        "Description": "Indicator of press-level accuracy",
        "Levels": {
            "correct": "participant responded with target on target breath or nontarget on pre-target breaths",
            "undershoot": "participant responded with target before target breath",
            "overshoot": "participant responded with target or nontarget after target breath",
            "selfcaught": "participant lost count and reset counter"
        }
    },

    # "cycle_accuracy": {
    #     "LongName": "Cycle accuracy",
    #     "Description": "Indicator of cycle-level accuracy",
    #     "Levels": {
    #         "correct": "participant estimated a nontarget trial",
    #         "undershoot": "participant estimated a target trial",
    #         "overshoot": "participant lost count and reset counter",
    #         "selfcaught": "participant lost count and reset counter"
    #     }
    # }

}

column_names = list(column_metadata.keys())
column_names.remove("press_accuracy")

sidecar = task_metadata | global_metadata | column_metadata

# column_names = ["cycle", ""]
# , "trial_accuracy", "trial_length", "rt_avg", "rt_std"]

target = 9
target_response = "right"
nontarget_response = "left"
reset_response = "space"
def press_accuracy(row):
    """Works as cycle accuracy too if take last row of each cycle.
    """
    if row["response"] == reset_response:
        return "selfcaught"
    elif row["response"] == target_response and row["press"] == target:
        return "correct"
    elif row["press"] > target:
        return "overshoot"
    elif row["press"] == target and row["response"] == nontarget_response:
        return "overshoot"
    elif row["press"] < target and row["response"] == nontarget_response:
        return "correct"
    elif row["press"] < target and row["response"] == target_response:
        return "undershoot"
    else:
        raise ValueError("Should never get here")

file_list = utils.find_source_files("bct", "json")

for file in file_list:
    with open(file, "r", encoding="utf-8") as f:
        subject_data = json.load(f)
    # convert cycle number strings to integers
    subject_data = { int(k): v for k, v in subject_data.items() }
    # remove practice cycles
    subject_data = { k: v for k, v in subject_data.items() if k < 900 }
    # remove final trial if it wasn't finished
    subject_data = { k: v for k, v in subject_data.items() if len(v) > 0 and v[-1][0] != "left" }
    # wrangle data
    # cycle_list = [ v for v in  ]
    rows = [ [i+1, j+1] + resp for i, cycle in enumerate(subject_data.values()) for j, resp in enumerate(cycle) ]
    df = pd.DataFrame(rows, columns=column_names)
    df["response_time"] = df["response_time"].diff().fillna(df["response_time"][0]).mul(1000)
    df["press_accuracy"] = df.apply(press_accuracy, axis=1)
    sub, ses, task = utils.filename2labels(file)
    basename = os.path.basename(file).replace(".json", "_beh.tsv").replace("_ses-001", "")
    data_filepath = os.path.join(utils.load_config().bids_root, sub, "beh", basename)
    utils.make_pathdir_if_not_exists(data_filepath)
    df.to_csv(data_filepath, index=False, sep="\t", float_format="%.0f")
    utils.pretty_sidecar_export(sidecar, data_filepath)