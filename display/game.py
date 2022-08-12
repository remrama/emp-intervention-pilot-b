"""A base class to use for a psychopy experiment.

It has essential stuff like opening a window,
setting up some text, some functions to show a message,
quit, save, send a slack message, and more.
"""
import os
import sys
import json
import inspect
import requests

from psychopy import prefs
prefs.hardware["audioLib"] = ["PTB", "sounddevice", "pyo", "pygame"]

from psychopy import core, visual, event, monitors, logging


# Load parameters from configuration file.
with open("./config.json", "r", encoding="utf-8") as f:
    C = json.load(f)


class Game(object):
    def __init__(self, subject_number, session_number, task_name):

        self.subject_number = subject_number
        self.session_number = session_number
        self.task_name = task_name
        self.generate_experiment_id()
        self.development_mode = subject_number == 999

        self.data_directory = C["data_directory"]

        self.data = {}
        self.passed_practice = False

        self.exit_message = "Thank you.\nYour responses have been recorded."

        self.quit_button = C["quit_button"]
        self.next_button = C["next_button"]

        self.monitor_params = {
            "distance_cm": 136,
            "width_cm": 85.7,
            "size_pix": [1024, 768],
        }
        self.window_params = {
            "size": [800, 800], # when not fullscreen
            "color": "gray", # background
            "screen": -1,
            "units": "deg",
            "fullscr": self.development_mode^1,
            "allowGUI": False,
            "checkTiming": True,
        }

        self.init_slack()
        self.init_exporting()
        self.init_window()
        self.init_stimuli()
        self.mouse = event.Mouse(self.win)

    def generate_experiment_id(self):
        self.experiment_id = "_".join([
            f"sub-{self.subject_number:03d}",
            f"ses-{self.session_number:03d}",
            f"task-{self.task_name}"
        ])

    def init_slack(self):
        with open("./slack_url.txt", "r") as f:
            self.slack_url = f.read().strip()

    def init_exporting(self):
        log_fname = os.path.join(self.data_directory, self.experiment_id+".log")
        if not self.development_mode:
            assert not os.path.exists(log_fname), f"{log_fname} can't already exist."
        logging.LogFile(log_fname, level=logging.INFO, filemode="w")
        self.json_fname = log_fname.replace(".log", ".json")
    
    def init_window(self):
        monitor = monitors.Monitor("testMonitor")
        monitor.setDistance(distance=self.monitor_params["distance_cm"])
        monitor.setWidth(width=self.monitor_params["width_cm"])
        monitor.setSizePix(self.monitor_params["size_pix"])
        self.win = visual.Window(monitor="testMonitor", **self.window_params)

    def init_stimuli(self):
        self.topText = visual.TextStim(self.win, name="topTextStim",
            pos=[0, 4], height=.5, wrapWidth=20, color="white")
        self.middleText = visual.TextStim(self.win, name="middleTextStim",
            pos=[0, 0], height=.5, wrapWidth=20, color="white")
        self.bottomText = visual.TextStim(self.win, name="bottomTextStim",
            text="Press [" + self.next_button + "] to continue",
            pos=[0, -4], height=.5, wrapWidth=20, color="white")
        self.fixationStim = visual.GratingStim(self.win, name="fixationStim",
            mask="cross", tex=None, size=[1, 1])

    def init_slack(self):
        with open("./slack_url.txt", "r") as f:
            self.slack_url = f.read().strip()

    def send_slack_notification(self, text):
        if not self.development_mode:
            text = self.experiment_id + ": " + text
            try:
                requests.post(self.slack_url, json=dict(text=text))
            except:
                pass

    def save_data(self):
        with open(self.json_fname, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, sort_keys=False)

    def quit(self, manual=False, soft=False):
        self.save_data()
        logging.flush()
        if manual:
            self.win.close()
            self.send_slack_notification("**MANUAL QUIT**")
            sys.exit(3) # would rather use core.quit but need the custom exit code
        else:
            self.show_message_and_wait_for_press(self.exit_message)
            self.win.close()
            self.send_slack_notification("Experiment ended")
            if soft: # to avoid sys.exit and run stuff afterwards
                logging.flush() # the only other important thing from core quit?
            else:
                core.quit()

    def check_for_quit(self):
        if event.getKeys(keyList=[self.quit_button]):
            self.quit(manual=True)

    def show_message_and_wait_for_press(self, text):
        self.middleText.text = inspect.cleandoc(text)
        self.middleText.draw()
        self.bottomText.setOpacity(.5)
        self.bottomText.draw()
        self.win.flip()
        core.wait(3)
        self.bottomText.setOpacity(1)
        event.clearEvents(eventType="keyboard")
        while not event.getKeys(keyList=[self.next_button]):
            self.middleText.draw()
            self.bottomText.draw()
            self.win.flip()
            self.check_for_quit()
