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

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_parser import config_parser
from db.db_tracker import DBTracker

config = config_parser()
db_path = config["DB"]["db_path"]
class ActionDBSync(Action):
    """Saves the tracker to the custom sqlite database"""
    def name(self) -> Text:
        return "action_db_sync"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        db = DBTracker(db_path)
        tracker_dict = DBTracker.tracker_to_dict(tracker)
        db.track_user(tracker_dict)
        print("action_db_sync")

        return []