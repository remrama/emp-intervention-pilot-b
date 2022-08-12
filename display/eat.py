"""Empathic Accuracy Task

Re-creating the Ong et al., 2019 task
in python for EEG triggers. The same
videos are used (freely available upon request).
Paper - https://doi.org/10.1109/TAFFC.2019.2955949
More info - https://github.com/desmond-ong/TAC-EA-model
"""
import os
import json
import inspect

from game import Game

from psychopy import visual


# Load parameters from configuration file.
with open("./config.json", "r", encoding="utf-8") as f:
    C = json.load(f)


class EmpathicAccuracyTask(Game):
    def __init__(self,
        subject_number,
        session_number,
        task_name,
        video_directory=C["video_directory"],
        practice_video_id=C["practice_video_id"],
        sample_rate=.5, # seconds response is sampled
        practice_too_long=30, # seconds they need to respond in while practicing
        ):
        super().__init__(subject_number, session_number, task_name)

        # Experiment parameters
        self.sample_rate = sample_rate
        self.practice_too_long = practice_too_long
        self.practice_video_id = practice_video_id
        self.video_directory = video_directory

        self.show_instructions = task_name.endswith("A")

        self.get_video_ids()
        self.load_video_paths()
        self.n_videos = len(self.task_video_ids)

        self.screen_text = dict(
            welcome=f"""
                Thank you for participating.

                As you watch the following {self.n_videos} videos,
                continuously rate how positive or negative you believe
                the speaker is feeling at every moment.
                """,

            prepractice="""
                Each video is about 2 minutes long.

                First we'll practice one to be sure the instructions are clear.
                """,

            redo_practice=f"""
                Let's try that again.

                If you have any questions, now is a
                good time to ask the experimenter.
                """,

            passed_practice=f"""
                Great!

                If you have any questions, now is a
                good time to ask the experimenter.
                """,

            instructions="""
                Please rate how you believe the person in the video is feeling at every moment in time,
                and remember to make your ratings throughout the video.

                When you are ready to begin, click on the green button to start the video.
                """,

            reminder="""
                Remember to continuously rate
                the speaker's emotions as the video plays.
                """,

            goodbye="""
                Your responses have been recorded.

                This part of the experiment is over.
                """,

        )
        self.screen_text = { k: inspect.cleandoc(v) for k, v in self.screen_text.items() }

        self.more_stims()

        self.send_slack_notification("Experiment started")


    def get_video_ids(self):
        video_set = self.task_name[-1]
        with open("./config.json", "r", encoding="utf-8") as f:
            C = json.load(f)
        self.task_video_ids = C[f"Set{video_set}_video_ids"]


    def load_video_paths(self):
        self.video_paths = {}
        for vid in [self.practice_video_id] + self.task_video_ids:
            basenames = [ bn for bn in os.listdir(self.video_directory) if bn.startswith(vid) ]
            assert len(basenames) == 1, f"Expected 1 file matching video id {vid}"
            bname = basenames[0]
            self.video_paths[vid] = os.path.join(self.video_directory, bname)


    def more_stims(self):

        self.headerText = visual.TextStim(self.win,
            name="TextStim-instructions",
            text=self.screen_text["instructions"],
            pos=[0, 8], height=.5, color="white",wrapWidth=20)

        self.reminderText = visual.TextStim(self.win,
            name="TextStim-reminder",
            text=self.screen_text["reminder"],
            pos=[0, 6], height=1, color="white", wrapWidth=20)

        self.playButton = visual.Rect(self.win,
            name="ShapeStim-play",
            width=1, height=1, pos=[0, -10],
            fillColor="green", lineColor="black", lineWidth=1)

        self.mov = visual.MovieStim3(self.win,
            name="MovieStim-temp", # gets updated later
            filename=self.video_paths[self.practice_video_id],
            pos=[0, 0])

        # 100 points between -1 and 1, sampled every .5 seconds
        self.slider = visual.Slider(self.win,
            name="SliderStim-emotion",
            pos=[0, -8],
            size=[8, .5], # width, height
            labelHeight=.5,
            ticks=[-1, 1], labels=["Very\nnegative", "Very\npositive"],
            startValue=0,
            flip=True, # to put labels on top
            granularity=0, # continuous
            color="black", # labels
            fillColor="black", # marker
            borderColor="black", # line and ticks
            readOnly=True,
        )



    def empathy_trial(self, movie_id, practice=False):

        # Load movie
        video_path = self.video_paths[movie_id]
        self.mov.name = f"MovieStim-{movie_id}"
        self.mov.loadMovie(filename=video_path, log=True)
        # movie_dims = [mov._mov.w, mov._mov.h]
        # print(movie_dims)
        # set by height
        # mov.setSize(movie_dims)

        # Reset slider
        self.slider.name = f"SliderStim-{movie_id}"
        self.slider.setReadOnly(False, log=True)
        self.slider.reset()

        trial_samples = []
        while self.mov.status != visual.FINISHED:
            if self.slider.responseClock.getTime() >= self.sample_rate*len(trial_samples):
                pos = self.slider.getMarkerPos() # does NOT require mouse up
                pos = float(round(pos, 2))
                trial_samples.append(pos)

            self.slider.draw()
            self.mov.draw()
            if practice: # Check if they've moved the slider recently.
                n_samples2get = int(self.practice_too_long/self.sample_rate)
                n_unique_recent_responses = len(set(trial_samples[-n_samples2get:]))
                if n_unique_recent_responses == 1:
                    self.reminderText.draw()
            self.win.flip()
            self.check_for_quit()

        self.mov.stop()
        self.slider.setReadOnly(True, log=True)
        self.data[movie_id] = trial_samples
        self.save_data()


    def iti(self): # Inter-trial-interval
        # Wait for play button to be clicked
        while not self.mouse.isPressedIn(self.playButton, buttons=[0]):
            self.headerText.draw()
            self.playButton.draw()
            self.slider.draw()
            self.win.flip()
            self.check_for_quit()

    def instructions(self):
        self.show_message_and_wait_for_press(self.screen_text["welcome"])
        self.show_message_and_wait_for_press(self.screen_text["prepractice"])

    def practice(self):
        while not self.passed_practice:
            self.iti()
            self.empathy_trial(self.practice_video_id, practice=True)
            # make sure there were at least a few responses
            self.check_practice_passed()
            if not self.passed_practice:
                self.show_message_and_wait_for_press(self.screen_text["redo_practice"])
            else:
                self.show_message_and_wait_for_press(self.screen_text["passed_practice"])

    def check_practice_passed(self):
        responses = self.data[self.practice_video_id]
        n_unique = len(set(responses))
        if n_unique > 5:
            self.passed_practice = True

    def task(self):
        for i, movie_id in enumerate(self.task_video_ids):
            self.iti()
            self.send_slack_notification(f"Video {i+1}/{self.n_videos} ({movie_id}) started")
            self.empathy_trial(movie_id)
            results_msg = self.calculate_performance(movie_id)
            slack_msg = f"Video {i+1}/{self.n_videos} ({movie_id}) ended" + "\n" + results_msg
            self.send_slack_notification(slack_msg)

    def calculate_performance(self, movie):
        samples = self.data[movie]
        scores = {
            "mean": float(sum(samples) / len(samples)),
            "min": float(min(samples)),
            "max": float(max(samples)),
        }
        msg = "\n".join([ f"Rating {k}: {v:.2f}" for k, v in scores.items() ])
        return msg


    def run(self):
        if self.show_instructions:
            self.instructions()
            self.practice()
        self.task()



if __name__ == "__main__":


    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", type=int, default=999)
    parser.add_argument("--session", type=int, default=1)
    parser.add_argument("--version", type=str, default="A", choices=["A", "B"])
    args = parser.parse_args()

    subject_number = args.subject
    session_number = args.session
    task_version = args.version

    task_name = "eat" + task_version

    eat = EmpathicAccuracyTask(subject_number, session_number, task_name=task_name)
    eat.run()
    eat.quit()
