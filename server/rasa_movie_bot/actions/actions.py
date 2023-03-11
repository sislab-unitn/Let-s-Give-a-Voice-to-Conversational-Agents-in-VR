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
tmdb.API_KEY = config['tmdb']['api_key']

from enum_actions import Actions
from enum_slots import Slots
from slots.enum_movie_or_tv import MovieOrTv
from tmdb_parser import TMDBParser

class ActionDiscoverMovie(Action):
    def name(self) -> Text:
        return Actions.ActionDiscoverMovie.value
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> Dict[Text, Any]:
        movie_or_tv = tracker.get_slot(Slots.movie_or_tv.value)
        
        if movie_or_tv is None:
            print(f'{Slots.movie_or_tv.value} not set')
            return {}

        genre_ids = TMDBParser.get_slot_ids(movie_or_tv)
        
        genre = tracker.get_slot(Slots.genre.value)
        if movie_or_tv == MovieOrTv.movie.value:
            if genre is None:
                discover = tmdb.Discover()
                response = discover.movie()
            else:   
                discover = tmdb.Discover()
                response = discover.movie(with_genres=genre_ids[genre])
        elif movie_or_tv == MovieOrTv.tv_show.value:
            if genre is None:
                discover = tmdb.Discover()
                response = discover.tv()
            else:   
                
                discover = tmdb.Discover()
                response = discover.tv(with_genres=genre_ids[genre])
        # top 3 results
        if response['total_results'] == 0:
            evt = SlotSet("top_names","")
            return [evt]
        else:
            results = response['results'][:3]
            try:
                top_names = [result['title'] for result in results]
            except KeyError:
                top_names = [result['name'] for result in results]
            top_names[-1] = "and " + top_names[-1]
            top_names = ", ".join(top_names)
            print(top_names)
            evt = SlotSet("top_names",top_names)
            # create a slot with the results
            # containing the title, and poster downloaded as image
            results_data = dict()
            results_data['images'] = []
            results_data['titles'] = []
            for result in results[:3]:
                try:
                    title = result['title']
                except KeyError:
                    title = result['name']
                results_data['titles'].append(title)
                poster_path = result['poster_path']
                if poster_path is not None:
                    poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
                    request = requests.get(poster_url,stream=False)
                    request.raise_for_status()
                    # encode in base64 and to utf-8 to get compatibility with json
                    encoded = base64.b64encode(request.content)
                    results_data['images'].append(encoded.decode('utf-8'))
                else:
                    results_data['images'].append(None)
            ent = SlotSet("results_data",results_data)
            return [evt,ent]


# add fallback is results are empty
class ActionGenresAvailable(Action):
    def name(self) -> Text:
        return "action_genres_available"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        movie_or_tv = tracker.get_slot('movie_or_tv')
        if movie_or_tv == None:
            print('movie or tv not set')
            return []
        genres = get_slot_ids(movie_or_tv)
        genres_available = list(genres.keys())
        genres_available[-1] = "and " + genres_available[-1]
        genres_available = ", ".join(genres_available)
        print(genres_available)
        evt = SlotSet("genres_available",genres_available)
        return [evt]
