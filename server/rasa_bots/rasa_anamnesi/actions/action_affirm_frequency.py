# This files contains your custom actions which can be used to run
# custom Python code.

# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

import os
import sys
from typing import List, Text, Dict, Any

from rasa_sdk import FormValidationAction, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
    )
)





class ValidateInvestigateForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_investigate_form"

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[Text]:
        print ("required_slots")
        additional_slots =  domain_slots.copy()
        # print (additional_slots)
        if tracker.slots.get("drink") is True and "drink_frequency" not in additional_slots:
            idx = additional_slots.index("drink")
            additional_slots.insert(idx+1, "drink_frequency")
        if tracker.slots.get("smoke") is True and "smoke_frequency" not in additional_slots:
            idx = additional_slots.index("smoke")
            additional_slots.insert(idx+1, "smoke_frequency")
        if tracker.slots.get("symptoms") is not None and "symptoms_confirmation" not in additional_slots:
            additional_slots.insert(1, "symptoms_confirmation")
            
            # dispatcher.utter_template("utter_ask_symptoms", tracker)
            
        # print (additional_slots)
        return additional_slots
    # def extract_symptoms(self, dispatcher, tracker, domain):
    #     print ("extract_symptoms")

    def validate_symptoms_confirmation(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print ("validate_symptoms_confirmation")
        if slot_value is False:
            return {"symptoms_confirmation": slot_value, "symptoms": None}
        else:
            return {"symptoms_confirmation": slot_value}