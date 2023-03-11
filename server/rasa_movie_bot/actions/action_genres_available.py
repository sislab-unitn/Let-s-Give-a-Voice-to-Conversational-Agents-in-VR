

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
)


from .enum_actions import Actions
from .enum_slots import Slots, MovieOrTv, Genre
from .tmdb_parser import TMDBParser

class ActionGenresAvailable(Action):
    """
    Class that runs the action to get the genres available
    """

    def name(self) -> Text:
        return Actions.ActionGenresAvailable.value

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        movie_or_tv = tracker.get_slot(Slots.movie_or_tv.value)
        # get the genres available
        genres_available = TMDBParser.discover_genres(movie_or_tv)
        # convert to string
        genres_available = TMDBParser.list_to_string(genres_available)
        # create a slot with the genres available
        evt = SlotSet(Slots.genres_available.value, genres_available)
        return [evt]
