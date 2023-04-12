# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import os
import sys
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))))



from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

class ActionExtractSymptoms(Action):
    def name(self) -> Text:
        return "action_extract_symptoms"
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        print ("action_extract_symptoms")
        # dispatcher.utter_message(text="Can you please tell me your symptoms?")
        text = tracker.latest_message.get("text")
        previous_symptoms = tracker.get_slot("symptoms")
        try:
            concat_symptoms = previous_symptoms + text
        except TypeError:
            concat_symptoms = text
        evt = SlotSet("symptoms", concat_symptoms)
        return [evt]