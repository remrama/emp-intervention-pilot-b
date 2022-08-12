"""Rapid Serial Visual Presentation task
but not Rapid!

Digits 1-9 are randomly presented at a slow rate.
Task is to press nontarget button on 1-8 and target button on 9.
"""
import os
import json
import random

from game import Game

from psychopy import core, visual, sound, event


with open("./config.json", "r", encoding="utf-8") as f:
    C = json.load(f)


class SerialVisualPresentation(Game):

    def __init__(self,
        subject_number,
        session_number,
        task_name="svp",
        task_length_mins=C["svp_task_length"],
        trial_length_secs=C["svp_trial_length"],
        trial_jitter_secs=C["svp_trial_jitter"],
        target_button="right",
        nontarget_button="left",
        digit_height=2,
        nontarget_digits=[1, 2, 3, 4, 5, 6, 7, 8],
        target_digit=9,
        practice_requirement=5, # number of trials in a row they need to get right to move on
        soundfile=os.path.join(C["audio_directory"], "svp-attention-trimmed.wav"),
        ):
        super().__init__(subject_number, session_number, task_name)

        # Timing/length (all in seconds)
        self.task_length = task_length_mins*60
        self.trial_length = trial_length_secs
        self.trial_jitter = trial_jitter_secs
        self.practice_requirement = practice_requirement
        self.digit_height = digit_height
        self.soundfile = soundfile

        self.data["practice"] = []
        self.data["task"] = []

        # Clocks
        self.taskClock = core.Clock()

        # Keyboard
        self.target_button = target_button
        self.nontarget_button = nontarget_button
        self.trial_keylist = [target_button, nontarget_button]

        self.instructions_text = [
            """
            In this task, we would like you to pay attention to a stream of numbers.
            
            When you see a """ + str(target_digit) + """ pop up, press the """ + self.target_button.capitalize() + """ Arrow button.
            For all other numbers, press the """ + self.nontarget_button.capitalize() + """ Arrow button.
            
            You should be pressing a button for every number that pops up.
            """,
        ]

        self.practice_instructions_text = "Press " + self.target_button.capitalize() + " Arrow when you see a " + str(target_digit) + ".\nPress " + self.nontarget_button.capitalize() + " Arrow for all other numbers."

        self.preaudio_message = """
            Before starting the task, please relax
            and listen to the following short recording.
            """

        self.post_practice_message = """
            Great job!

            The next """ + str(task_length_mins) + """ minutes will be this same task
            but without feedback on your performance.
            """

        self.pretask_message = """
            The task will begin now.

            Please reflect on those ideas presented to you while responding to the numbers.

            The task will last about """ + str(task_length_mins) + """ minutes.
            
            A message will appear on screen to let you know when the time is up.
            If you have any questions, you should ask the experimenter at this time.
            """

        self.nontarget_digits = nontarget_digits
        self.target_digit = target_digit
        self.all_digits = nontarget_digits + [target_digit]


        self.digit_sequence = [] # generated on the fly
        # self._generate_random_stim_sequence(practice=True)
        # self.trial_counter = 0

        self.more_stims()

    def more_stims(self):
        self.digitStim = visual.TextStim(self.win, name="digitStim",
            pos=[0, 0], height=self.digit_height, color="white")
        self.audioStim = sound.Sound(self.soundfile, name="audioStim")

    def _generate_digit_stim(self):
        if self.digit_sequence:
            if not any(map(lambda x: x==self.target_digit, self.digit_sequence[-self.practice_requirement:])):
                digit = 9
            else:
                last_digit = self.digit_sequence[-1]
                possible_digits = [ d for d in self.all_digits if d != last_digit ]
                digit = random.choice(possible_digits)
        else:
            digit = random.choice(self.all_digits)
        return digit

    # def _generate_random_stim_sequence(self, practice=False):
    #     # If it's practice, want to make sure they get a 9
    #     # accurately as well as the accuracy streak, so make
    #     # sure there is always a 9 within the required
    #     # accuracy streak window.
    #     # Generate a sequence that is way too long to actually reach.
    #     possible_digits = self.nontarget_digits + [self.target_digit]
    #     weights = np.append(np.ones_like(self.nontarget_digits), self.target_pweight)
    #     weights = weights/weights.sum()
    #     # if practice:
    #     # figure out the max possible trial count, which wouldnt' realistically be reached
    #     min_trial_length = self.trial_length - self.trial_jitter
    #     max_trial_count = int(self.task_length / min_trial_length)
    #     self.digit_sequence = np.random.choice(possible_digits,
    #         size=max_trial_count, replace=True, p=weights)

    def play_audio(self):
        self.show_message_and_wait_for_press(self.preaudio_message)
        self.fixationStim.draw()
        self.audioStim.play()
        self.win.flip()
        while self.audioStim.status != visual.FINISHED:
            self.check_for_quit()

    def single_trial(self, practice=False):
        # Get the timing for this trial
        current_jitter = random.uniform(-self.trial_jitter, self.trial_jitter)
        current_length = self.trial_length + current_jitter
        # current_digit = self.digit_sequence[self.trial_counter]
        # if practice:
        #     if len(self.prior_stims) >= self.practice_requirement:
        #         # make sure a 9 comes up in the streak
        #         if self.target_digit not in self.prior_stims[-self.practice_requirement:]:
        #             current_digit = self.target_digit
        current_digit = self._generate_digit_stim()
        self.digitStim.text = current_digit
        self.digit_sequence.append(current_digit)
        event.clearEvents(eventType="keyboard")
        response = None
        t0 = self.taskClock.getTime() # self.data["task"][-1][1]
        while self.taskClock.getTime() - t0 < current_length:
            self.digitStim.draw()
            self.win.flip()
            if response is None:
                for response in event.getKeys(keyList=self.trial_keylist, timeStamped=self.taskClock):
                    self.digitStim.bold = True
                    key, rt = response
                    accurate = (key == self.nontarget_button
                            and current_digit in self.nontarget_digits
                        ) or (key == self.target_button
                            and current_digit == self.target_digit
                        )
                    response += (accurate,)
                    if not self.passed_practice:
                        if accurate:
                            self.digitStim.color = "green"
                        else:
                            self.digitStim.color = "red"
            self.check_for_quit()

        if response is None:
            response = [None, None, None]

        # self.trial_counter += 1
        self.digitStim.bold = False
        if not self.passed_practice:
            self.digitStim.color = "white"

        if not self.passed_practice:
            self.data["practice"].append(response)
        else:
            self.data["task"].append(response)

    def task(self):
        # the main/full task
        # self._generate_random_stim_sequence()
        # self.trial_counter = 0
        self.show_message_and_wait_for_press(self.pretask_message)
        self.send_slack_notification("SVP Task started")
        self.prior_stims = []
        self.taskClock.reset()
        while self.taskClock.getTime() < self.task_length-self.trial_length:
            self.single_trial()
            self.save_data()


    def practice(self):
        self.send_slack_notification("SVP Practice started")
        self.topText.text = self.practice_instructions_text
        self.topText.setAutoDraw(True)
        while not self.passed_practice:
            self.single_trial(practice=True)
            self.check_practice_passed()
        self.topText.setAutoDraw(False)
        self.show_message_and_wait_for_press(self.post_practice_message)

    def check_practice_passed(self):
        responses = self.data["practice"]
        if len(responses) > self.practice_requirement:
            _, _, accuracy = zip(*responses[-self.practice_requirement:])
            accuracy = [ x==True for x in accuracy ] # to knock out Nones
            pct_correct = sum(accuracy) / len(accuracy)
            print(pct_correct)
            if pct_correct >= .7:
                self.passed_practice = True

    def instructions(self):
        for txt in self.instructions_text:
            self.show_message_and_wait_for_press(txt)


    def run(self):
        self.instructions()
        self.practice()
        self.play_audio()
        self.task()


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", type=int, default=999)
    parser.add_argument("--session", type=int, default=999)
    args = parser.parse_args()

    subject_number = args.subject
    session_number = args.session

    svp = SerialVisualPresentation(subject_number, session_number)
    svp.run()
    svp.quit()
