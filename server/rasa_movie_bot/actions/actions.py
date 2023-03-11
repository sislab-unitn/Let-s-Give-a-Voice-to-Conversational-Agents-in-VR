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

import os, sys

import tmdbsimple as tmdb

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config_parser import config_parser

config = config_parser()
tmdb.API_KEY = config["server"]["tmdb_API"]

from .enum_actions import Actions
from .enum_slots import Slots, MovieOrTv, Genre
from .tmdb_parser import TMDBParser


from .action_discover_movies import ActionDiscoverMovie
from .action_genres_available import ActionGenresAvailable
from .action_movie_tv_form_validation import ValidateMovieTvForm
from .action_movie_tv_genre_form_validation import ValidateMovieTvGenreForm


