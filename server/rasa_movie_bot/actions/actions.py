# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
)
import requests
import pathlib
import os, sys
import toml
import base64

import tmdbsimple as tmdb

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_parser import config_parser

config = config_parser()
tmdb.API_KEY = config["server"]["tmdb_API"]

from enum_actions import Actions
from enum_slots import Slots, MovieOrTv, Genre
from tmdb_parser import TMDBParser

from validation_actions import ValidateMovieTvGenreForm


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

        genre = TMDBParser.genre_matcher(genre, movie_or_tv)

        response = TMDBParser.discover(movie_or_tv, genre)[:3]

        top_names = TMDBParser.response_to_names(response)

        evt = SlotSet(Slots.top_results.value, TMDBParser.list_to_string(top_names))

        return [evt]


# add fallback is results are empty
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
