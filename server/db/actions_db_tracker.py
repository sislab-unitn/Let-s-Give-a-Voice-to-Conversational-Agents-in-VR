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

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_parser import config_parser
from db.db_tracker import DBTracker

config = config_parser()
db_path = config["DB"]["db_path"]


class ActionDBSync(Action):
    """Saves the tracker to the custom sqlite database"""

    def name(self) -> Text:
        return "action_db_sync"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        db = DBTracker(db_path)
        tracker_dict = DBTracker.tracker_to_dict(tracker)
        db.track_user(tracker_dict)
        print("action_db_sync")

        return []


class RetrieveDBSync(Action):
    """Retrieves the next slot from the custom sqlite database if present and sets it in the tracker"""

    def name(self) -> Text:
        return "action_retrieve_db_sync"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        db = DBTracker(db_path)
        tracker_dict = DBTracker.tracker_to_dict(tracker)
        sender_id = tracker_dict["sender_id"]
        slots = db.get_slots(sender_id)
        requested_slot = tracker.get_slot("requested_slot")
        try:
            value = slots[requested_slot]
        except KeyError:
            value = None
        if requested_slot is not None and tracker.get_slot(requested_slot) is None:
            evt = SlotSet(requested_slot, value)
            print(evt)
        # print(tracker.slots)
        print("action_retrieve_db_sync")
        # print(requested_slot, value)
        return [evt]
class RetrieveDBAllSync(Action):
    """Retrieves all the slots from the custom sqlite database if present and sets it in the tracker"""

    def name(self) -> Text:
        return "action_retrieve_db_all_sync"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        db = DBTracker(db_path)
        tracker_dict = DBTracker.tracker_to_dict(tracker)
        sender_id = tracker_dict["sender_id"]
        slots = db.get_slots(sender_id)
        events = []
        for slot_name, value in slots.items():
            if tracker.get_slot(slot_name) is None and slot_name in tracker.slots.keys():
                evt = SlotSet(slot_name, value)
                events.append(evt)
        return events
class RetrieveDBSyncSymptoms(Action):
    """Retrieves symptoms slots from the custom sqlite database if present and sets it in the tracker"""

    def name(self) -> Text:
        return "action_retrieve_symptoms_db_sync"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print ("action_retrieve_symptoms_db_sync")
        db = DBTracker(db_path)
        tracker_dict = DBTracker.tracker_to_dict(tracker)
        sender_id = tracker_dict["sender_id"]
        slots = db.get_slots(sender_id)
        try:
            symptoms = slots["symptoms"]
        except KeyError:
            symptoms = None
        evt = SlotSet("symptoms", symptoms)
        return [evt]
