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

from config_parser import config_parser

config = config_parser()
tmdb.API_KEY = config["tmdb"]["api_key"]

from enum_actions import Actions
from enum_slots import Slots, MovieOrTv, Genre
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

        response = TMDBParser.discover(movie_or_tv, genre)

        # top 3 results
        if response[Slots.top_results.value] == 0:
            evt = SlotSet(Slots.top_results.value, None)
            return evt
        else:
            results = response["results"][:3]
            try:
                top_names = [result["title"] for result in results]
            except KeyError:
                top_names = [result["name"] for result in results]

            top_names[-1] = "and " + top_names[-1]
            top_names = ", ".join(top_names)
            print(top_names)
            evt = SlotSet("top_names", top_names)
            # create a slot with the results
            # containing the title, and poster downloaded as image
            results_data = dict()
            results_data["images"] = []
            results_data["titles"] = []
            for result in results[:3]:
                try:
                    title = result["title"]
                except KeyError:
                    title = result["name"]
                results_data["titles"].append(title)
                poster_path = result["poster_path"]
                if poster_path is not None:
                    poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
                    request = requests.get(poster_url, stream=False)
                    request.raise_for_status()
                    # encode in base64 and to utf-8 to get compatibility with json
                    encoded = base64.b64encode(request.content)
                    results_data["images"].append(encoded.decode("utf-8"))
                else:
                    results_data["images"].append(None)
            ent = SlotSet("results_data", results_data)
            return evt, ent


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
