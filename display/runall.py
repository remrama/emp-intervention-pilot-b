"""Use this run a complete behavioral subject.
It runs the empathic accuracy task before and after
an intervention task. The intervention task is picked
based on the subject number being odd or even.
"""
import argparse

from bct import BreathCountingTask
from eat import EmpathicAccuracyTask
from svp import SerialVisualPresentation

parser = argparse.ArgumentParser()
parser.add_argument("--subject", type=int, required=True)
parser.add_argument("--session", type=int, default=1)
args = parser.parse_args()

subject_number = args.subject
session_number = args.session

assert 1 <= subject_number <= 999, "Subject number needs to be between 1 and 999."
assert 1 <= session_number <= 999, "Session number needs to be between 1 and 999."

game1 = EmpathicAccuracyTask(subject_number, session_number, task_name="eatA")
game1.run()
game1.quit(soft=True)

if subject_number % 2 == 0: # even subject numbers
    game2 = SerialVisualPresentation(subject_number, session_number)
else:
    game2 = BreathCountingTask(subject_number, session_number)
game2.run()
game2.quit(soft=True)

game3 = EmpathicAccuracyTask(subject_number, session_number, task_name="eatB")
game3.run()
game3.quit(soft=True)
