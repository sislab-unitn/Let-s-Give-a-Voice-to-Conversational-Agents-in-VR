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




class ActionExtractWholeUtterance(Action):
    def name(self) -> Text:
        return "action_extract_whole_utterance"
    def run( self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        print ("action_extract_whole_utterance")
        text = tracker.latest_message.get("text")
        requested_slot = tracker.get_slot("requested_slot")
        if requested_slot is not None and tracker.get_slot(requested_slot) is None:
            evt = SlotSet(requested_slot, text)
            print (evt)
        print(tracker.slots)
        return [evt]