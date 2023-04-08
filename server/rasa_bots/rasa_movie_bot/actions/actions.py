# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import os
import sys
from typing import Any, Dict, List, Text

import tmdbsimple as tmdb
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

# add this folder to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_parser import config_parser

config = config_parser()
tmdb.API_KEY = config["server"]["tmdb_API"]

from action_discover_movies import ActionDiscoverMovie
from action_genres_available import ActionGenresAvailable
from action_movie_tv_form_validation import ValidateMovieTvForm
from action_movie_tv_genre_form_validation import ValidateMovieTvGenreForm
from enum_actions import Actions
from enum_slots import Genre, MovieOrTv, Slots
from tmdb_parser import TMDBParser


