# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import os
import sys
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))))


from db.actions_db_tracker import ActionDBSync
from .action_symptoms_slot import ActionExtractSymptoms
from .action_affirm_frequency import ValidateInvestigateForm