import os
import sys
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

# add this folder to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enum_actions import Actions
from enum_slots import Genre, MovieOrTv, Slots
from tmdb_parser import TMDBParser


class ActionDiscoverMovie(Action):
    """ActionDiscoverMovie Action to discover movies or tv shows"""

    def name(self) -> Text:
        return Actions.ActionDiscoverMovie.value

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        movie_or_tv = tracker.get_slot(Slots.movie_or_tv.value)
        genre = tracker.get_slot(Slots.genre.value)

        genre,_ = TMDBParser.genre_matcher(genre, movie_or_tv)

        response = TMDBParser.discover(movie_or_tv, genre)
        
        top_names = TMDBParser.response_to_names(response,3)

        evt = SlotSet(Slots.top_results.value, TMDBParser.list_to_string(top_names))

        return [evt]