"""Breath Counting Task in PsychoPy.

Modeled after:
    - Levinson et al., 2014     https://doi.org/10.3389/fpsyg.2014.01202
    - Wong et al., 2018         https://doi.org/10.1007/s12671-017-0880-1
"""
import os
import json
import inspect
import argparse

from game import Game

from psychopy import core, visual, sound, event, logging


with open("./config.json", "r", encoding="utf-8") as f:
    C = json.load(f)

audio_fname = os.path.join(C["audio_directory"], "bct-compassion.wav")


class BreathCountingTask(Game):

    def __init__(self,
        subject_number,
        session_number,
        task_name="bct",
        target_digit=9, # number of presses!
        task_length_mins=C["bct_task_length"],
        min_press_gap=1, # minimum seconds between presses that triggers warning in practice
        soundfile=audio_fname, # fullpath of file to play before task
        ):
        super().__init__(subject_number, session_number, task_name)


        self.task_ended = False

        # Timing/length
        self.target_digit = target_digit
        self.task_length = task_length_mins * 60
        self.min_press_gap = min_press_gap

        # Keyboard
        self.target_button = "right"
        self.nontarget_button = "left"
        self.reset_button = "space"

        self.soundfile = soundfile

        self.taskClock = core.Clock() # gets reset when real task starts

        self.min_opacity = .1 # for the text/arrows during practice

        self.preaudio_message = """
            Before starting the task, please relax
            and listen to the following short recording.
            """
        self.post_practice_message = """
            Great!

            During the full task, you will not have the visual help from the bottom arrows.

            You will only see the center cross, but continue to count your breaths and press the buttons.
            """
        self.pretask_message = """
            The task will begin now.

            Please reflect on those ideas presented to you while counting your breaths.

            The task will last about """ + str(task_length_mins) + """ minutes,
            no matter what pace you breathe or how accurate you are at counting.
            
            Remember to sit in a comfortable position, focus primarily on your breathing,
            and you can press """ + self.reset_button.capitalize() + """ to reset the counter if you lose track.

            A message will appear on screen to let you know when the time is up.
            If you have any questions, you should ask the experimenter at this time.
            """
        restart_txt = """Let's restart the counter."""

        practice_instructions = """
            Press the """ + self.nontarget_button.capitalize() + " Arrow with breaths 1-" + str(self.target_digit-1) + """,
            and the """ + self.target_button.capitalize() + " Arrow with breath " + str(self.target_digit) + """.

            Press """ + self.reset_button.capitalize() + """ and restart the count at 1 if you lose track.
            """
        # practice_instructions = "Breathe slowly and keep count of your breaths.\nPress " + self.nontarget_button.capitalize() + " Arrow on breaths 1-" + str(self.target_digit-1) + ".\nPress " + self.target_button.capitalize() + " Arrow on breath " + str(self.target_digit) + ".\nRestart the count.",
        
        self.header_text = {
            "fast": "That breath was too fast.",
            "early": "Don't press the " + self.target_button.capitalize() + " Arrow until count " + str(self.target_digit) + "." + "\n\n" + restart_txt,
            "late": "Remember to press the " + self.target_button.capitalize() + " Arrow on count " + str(self.target_digit) + "." + "\n\n" + "The count will not reset until " + self.target_button.capitalize() + " or " + self.reset_button.capitalize() + " is pressed.",
            "instructions": practice_instructions,
        }

        self.INSTRUCTIONS_MESSAGES = [
            """
            In the next task, we would like you to be aware of your breath.
            
            Please be aware of the movement of breath in and out
            in the space below your nose and above your upper lip
            (or any other aspect of your breath).

            There's no need to control the breath.
            Just breathe at a comfortable slow pace.
            """,
            """
            At some point, you may notice
            your attention has wandered from the breath.
            
            That's okay. Just gently place it back on the breath.
            """,
            """
            To help attention stay with the breath,
            you'll use a small part of your attention
            to silently count breaths from 1 to """ + str(self.target_digit) + """, again and again.
            
            An in and out breath together makes one count.

            Say the count softly in your mind so it only gets a little attention,
            while most of the attention is on feeling the breath.
            """,
            """
            Press the """ + self.nontarget_button.capitalize() + " Arrow on breaths 1-" + str(self.target_digit-1) + """,
            and the """ + self.target_button.capitalize() + " Arrow on breath " + str(self.target_digit) + """.
            This means you'll be pressing a button with each breath.

            If you find that you have forgotten the count,
            just press """ + self.reset_button.capitalize() + """ and restart the count at 1 with the next breath.

            Do not count the breaths using your fingers but only in your head.
            """,
            """
            We suggest you sit in an upright,
            relaxed posture that feels comfortable.

            Please keep your eyes at least partially open
            and directed at the screen during the experiment.
            """,
        ]

        self.final_message = """
            Great job :)

            This part of the experiment is over.
            """

        self.more_stims()

        self.send_slack_notification("Experiment started")


    def more_stims(self):
        self.audioStim = sound.Sound(self.soundfile, name="audioStim")

        arrowVert = [ # for upward-facing arrow, centered so it can be rotated
            (-.1,  .2), # top-left tail rect
            (-.1, -.4), # bottom-left tail rect
            ( .1, -.4), # bottom-right tail rect
            ( .1,  .2), # top-right tail rect
            ( .3,  .2), # bottom-right head triangle
            (  0,  .4), # head triangle tip
            (-.3,  .2), # bottom-left head triangle
        ]

        ARROWS_YLOC = -5 # vis degrees below central fixation
        TEXT_YLOC = -3.5 # vis degrees below central fixation

        # The stim numbers on bottom of screen for instructions/practice.
        # subtract mean to center them
        digit_xpositions = [ i-(sum(range(self.target_digit))/self.target_digit) for i in range(self.target_digit) ]
        self.digitsArrows = [ visual.ShapeStim(self.win,
                name=f"Arrow{i+1}ShapeStim",
                vertices=arrowVert,
                pos=[digit_xpositions[i], ARROWS_YLOC],
                size=1,
                ori= 90 if i+1==self.target_digit else -90,
                fillColor="black", lineColor="black")
            for i in range(self.target_digit) ]
        self.digitsTexts = [ visual.TextStim(self.win,
                name=f"Digit{i+1}TextStim",
                text=i+1,
                pos=[digit_xpositions[i], TEXT_YLOC],
                color="black")
            for i in range(self.target_digit) ]



    def flutter_fixation(self):
        """flutter opacity just to know something registered.
        """
        MAX_OPACITY = 1
        MIN_OPACITY = .5
        DURATION = .1 # seconds
        refresh_rate = self.win.monitorFramePeriod # seconds, should be about .016 (1/60)
        total_opacity_change = MAX_OPACITY - MIN_OPACITY
        n_flips = DURATION / refresh_rate
        opacity_change_per_flip = total_opacity_change / n_flips
        # self.fixationStim.setOpacity(MAX_OPACITY)
        while self.fixationStim.opacity > MIN_OPACITY:
            self.fixationStim.opacity -= opacity_change_per_flip
            self.fixationStim.draw()
            self.win.flip()
        while self.fixationStim.opacity < MAX_OPACITY:
            self.fixationStim.opacity += opacity_change_per_flip
            self.fixationStim.draw()
            self.win.flip()

    def play_audio(self):
        self.show_message_and_wait_for_press(self.preaudio_message)
        self.fixationStim.draw()
        self.audioStim.play()
        self.win.flip()
        while self.audioStim.status != visual.FINISHED:
            self.check_for_quit()

    def show_instructions(self):
        for msg in self.INSTRUCTIONS_MESSAGES:
            self.show_message_and_wait_for_press(msg)


    def reset_cycle(self):
        self.cycle_counter += 1
        self.breath_counter = 1
        self.cycle_responses = []
        self.save_data()

    def single_cycle(self):
        # Collect responses until participant ends cycle with target press or reset.
        cycle_ended = False
        while (not cycle_ended) and (not self.task_ended):
            response = self.collect_response()
            if response is not None:
                self.cycle_responses.append(response)
                self.breath_counter += 1
                if self.target_button in response or self.reset_button in response:
                    cycle_ended = True
        # Get cycle stats (accuracy to save and others to slack)
        # Save
        self.data[self.cycle_counter] = self.cycle_responses
        self.reset_cycle()

    def change_practice_screen(self, text_key):
        arrow_color = "green" if text_key == "instructions" else "red"
        text_color = "white" if text_key == "instructions" else "black"
        current_index = self.breath_counter - 1
        if current_index < self.target_digit:
            # can't draw anymore, they need to reset.
            self.digitsArrows[current_index].setColor(arrow_color)
            self.digitsArrows[current_index].setOpacity(1)
            self.digitsTexts[current_index].setOpacity(1)
        self.topText.text = inspect.cleandoc(self.header_text[text_key])
        self.topText.setColor(text_color)

    def collect_response(self):
        """Wait for a response and record it.
        Return keypress if a valid press.
        Return None if experiment is over.
        Quit if manual exit (push quit button).
        """
        self.fixationStim.draw() # could autodraw
        self.win.flip()
        while not self.task_ended: # returns out after press
            for response in event.getKeys(keyList=[self.target_button,
                                                   self.nontarget_button,
                                                   self.reset_button],
                                          timeStamped=self.taskClock):
                #### A buttons is pressed!
                self.flutter_fixation()
                if not self.passed_practice:
                    txt_key = "instructions"
                    key, timestamp = response
                    if self.breath_counter < self.target_digit and key == self.target_button:
                        txt_key = "early"
                    elif self.breath_counter == self.target_digit and key == self.nontarget_button:
                        txt_key = "late"
                    elif self.cycle_responses:
                        rt = timestamp - self.cycle_responses[-1][-1]
                        if rt < self.min_press_gap:
                            txt_key = "fast"
                    self.change_practice_screen(text_key=txt_key)

                return response

            # check for reasons to exit
            self.check_for_quit()
            if self.passed_practice and self.taskClock.getTime() > self.task_length:
                self.task_ended = True



                #     return response
        # press_clock.reset()
        # keyboard.clearEvents()
        # if task_clock.getTime() < total_task_length:
        #     max_wait = total_task_length - task_clock.getTime()
        # else:
        #     max_wait = 4
        # press = event.waitKeys(maxWait=max_wait, keyList=ALL_KEYS, timeStamped=task_clock, clearEvents=True)
        # print(press)
        # if press[0] == "left":
        #     quit()
        # pressed = False
        # while not pressed:
        #     for press in []:
        #         if press:
        #             print(press)
        #             pressed = True
        #             if press_clock.getTime() < MIN_PRESS_GAP:
        #                 print("TOO EARLY")
        #             else:
        #                 if press.char == "left":
        #                     accurate = True
        #                 elif press.char == "right":
        #                     accurate = False
        #                 elif press.char == "q":
        #                     quit()


    # def reset_practice(self, mistake):
    #     warning_msg = self.WARNING_MESSAGES[mistake]
    #     self.warningText.text = inspect.cleandoc(warning_msg)
    #     self.warningText.draw()
    #     self.win.flip()
    #     core.wait(self.min_reading_time*2)
    #     self.breath_counter = 1
    #     for tstim, astim in zip(self.digitsTexts, self.digitsArrows):
    #         tstim.setOpacity(self.min_opacity)
    #         astim.setOpacity(self.min_opacity)
    def check_practice_passed(self):
        # make sure they got 1 series of trials right
        if len(self.data) >= 2:
            last2 = list(self.data.values())[-2:]
            if all([ len(x)==self.target_digit for x in last2 ]):
                self.passed_practice = True
            ###! !!!! doesn't check for reset button

    def adjust_practice_stim_autodraws(self, autodraw):
        self.topText.setAutoDraw(autodraw)
        for tstim, astim in zip(self.digitsTexts, self.digitsArrows):
            tstim.setAutoDraw(autodraw)
            astim.setAutoDraw(autodraw)

    def practice(self):
        # self.fixationStim.setAutoDraw(True)
        # self.topText.setAutoDraw(True)
        # for tstim, astim in zip(self.digitsTexts, self.digitsArrows):
        #     tstim.setAutoDraw(True)
        #     astim.setOpacity(True)
        self.topText.text = inspect.cleandoc(self.header_text["instructions"])
        self.adjust_practice_stim_autodraws(autodraw=True)
        while not self.passed_practice:
            # reset helper stims
            for tstim, astim in zip(self.digitsTexts, self.digitsArrows):
                astim.setColor("black")
                astim.setOpacity(self.min_opacity)
                tstim.setOpacity(self.min_opacity)
            self.single_cycle()
            # hang onto end screen at end of cycle so they see the arrow
            self.fixationStim.draw() # others are on auto
            self.win.flip()
            core.wait(1)
            self.check_practice_passed()
        self.adjust_practice_stim_autodraws(autodraw=False)
        self.show_message_and_wait_for_press(self.post_practice_message)

    def task(self):
        self.show_message_and_wait_for_press(self.pretask_message)
        self.send_slack_notification("Task started")
        logging.log(level=logging.INFO, msg="Main task started")
        self.taskClock.reset()
        while not self.task_ended:
            self.single_cycle()

    def run(self):
        self.show_instructions()
        self.cycle_counter = 900
        self.reset_cycle()
        self.practice()
        self.play_audio()
        self.cycle_counter = 0
        self.reset_cycle()
        self.task()

    # def calculate_performance(results_list, last_trial_only=False):
    #     df = pd.DataFrame(results_list).set_index("trial")
    #     if last_trial_only:
    #         df = df.loc[df.index.max()]
    #     accuracy = df.groupby("trial").last(
    #         )["accuracy"].eq("correct").mean()
    #     return accuracy


# def determine_press_accuracy(k, count):
#     """
#     - correct (right press on breath 9
#                OR left press on breath < 9)
#     - miscount (right press on breath not 9)
#     - overcount (left press on breath > 9)
#     - reset (press spacebar)
#     """
#     if k == KEY_CODES["reset"]:
#         accuracy = "reset"
#     elif k == KEY_CODES["9"]:
#         accuracy = "correct" if count == TRIAL_LENGTH else "miscount"
#     elif k == KEY_CODES["1-8"]:
#         accuracy = "correct" if count < TRIAL_LENGTH else "overcount"
#     else:
#         raise ValueError(f"How did {k} get pressed?!")
#     return accuracy


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", type=int, default=999)
    parser.add_argument("--session", type=int, default=1)
    args = parser.parse_args()

    subject_number = args.subject
    session_number = args.session

    bct = BreathCountingTask(subject_number, session_number)
    bct.run()
    bct.quit()

    # # Practice until performance is good.
    # pass_practice = False
    # # keep a running count of just one trial
    # results = []
    # press_counter = 1
    # while not pass_practice:
    #     keypress = single_press()
    #     key, rt = keypress
    #     accuracy = determine_press_accuracy(key, press_counter)
    #     if press_counter > 9:
    #         reset()
    #     if rt < MIN_PRESS_GAP:
    #         too_fast_txt.draw()
    #         win.flip()
    #         core.wait(WARNING_MSG_LENGTH)


    # # Start task.
    # press_counter = 1
    # trial_counter = 1
    # results = []
    # # Bc of practice, want to be able to score a "trial".
    # # task_clock.reset()
    # while taskCountdown.getTime() > 0:
    #     keypress = single_press()
    #     if keypress: # None if there's no time left
    #         key, rt = keypress
    #         accuracy = determine_press_accuracy(key, press_counter)
    #         print("Press:", accuracy)
    #         trial_data = {
    #             "trial": trial_counter,
    #             "press": press_counter,
    #             "key": key,
    #             "rt": round(rt, 3),
    #             "accuracy": accuracy,
    #         }
    #         results.append(trial_data)
    #         trial_data_string = json.dumps(trial_data)
    #         logging.log(level=logging.INFO, msg=trial_data_string)
    #         logging.flush()

    #         if key in [KEY_CODES["reset"], KEY_CODES["9"]]:
    #             trial_counter += 1 # advance trial counter
    #             press_counter = 1 # reset press/breath counter
    #             # Trial-level accuracy is whatever the last press accuracy was
    #             trial_correct = accuracy=="correct"
    #             # acc = calculate_performance(results)
    #             print("Trial:", trial_correct)
    #         else:
    #             press_counter += 1 # advance press/breath counter