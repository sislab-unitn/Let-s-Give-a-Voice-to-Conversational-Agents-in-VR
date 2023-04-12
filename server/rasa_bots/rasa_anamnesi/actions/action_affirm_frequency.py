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

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
    )
)


from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from typing import Text, List, Optional

from rasa_sdk.forms import FormValidationAction


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
        print (additional_slots)
        if tracker.slots.get("drink") is True:
            idx = additional_slots.index("drink")
            additional_slots.insert(idx+1, "drink_frequency")
        if tracker.slots.get("smoke") is True:
            idx = additional_slots.index("smoke")
            additional_slots.insert(idx+1, "smoke_frequency")
        print (additional_slots)
        return additional_slots

    def validate_drink(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        print("validate_drink")
        
        return {"drink": slot_value}
        if slot_value is True:
            return {"drink_frequency": None}
        else:
            return {"drink_frequency": None}
