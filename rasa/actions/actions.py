# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
    UserUtteranceReverted,
    ConversationPaused,
    EventType,
)
import tmdbsimple as tmdb
import Levenshtein
import requests
import argparse
import pathlib
import os, sys
import toml
import io
import base64

# check if config file exists
current_path = pathlib.Path(__file__).parent.absolute()
config_toml = "config.toml"
config_path = os.path.join(current_path, config_toml)
print(config_path)
if not os.path.exists(config_path):
    print(f"{config_toml} file not found in the default path in the server directory")
    sys.exit(1)

# read config file
with open(config_path, mode="r") as f:
    config = toml.load(f)

tmdb.API_KEY = config["server"]["tmdb_API"]
# 5 seconds timeout for requests to avoid blocking
tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read
tmdb.REQUESTS_SESSION = requests.Session()
# complete a search to ensure that the API key is valid and the connection is working
__ = tmdb.Discover()


# function to get the slot ids
def get_slot_ids(movie_or_tv) -> Dict:
    genre = tmdb.Genres()
    genres = {}
    if movie_or_tv == "movie":
        for item in genre.movie_list()["genres"]:
            genres[item["name"]] = str(item["id"])
    else:
        for item in genre.tv_list()["genres"]:
            genres[item["name"]] = str(item["id"])
    return genres


def genre_matcher(selected_genre, movie_or_tv):
    print(selected_genre)
    selected_genre = selected_genre.lower()
    genres_og = get_slot_ids(movie_or_tv)
    inverse_genres = {v: k for k, v in genres_og.items()}
    genres_lower = {}
    for key, item in genres_og.items():
        genres_lower[key.lower()] = item
    similarity = {}
    for genre_lower in genres_lower:
        for word in genre_lower.split():
            try:
                if selected_genre == word:
                    return inverse_genres[genres_lower[genre_lower]], 1
                similarity[genre_lower][0] = max(
                    Levenshtein.jaro(selected_genre, word), similarity[genre_lower][0]
                )
            except KeyError:
                similarity[genre_lower] = [
                    Levenshtein.jaro(selected_genre, word),
                    genres_lower[genre_lower],
                ]
    # max similarity
    similarity_mx = max(similarity, key=lambda x: similarity[x][0])
    inverse_similarity = {v[0]: k for k, v in similarity.items()}
    similarity_value = max(inverse_similarity, key=lambda x: x)
    similarity_id = similarity[similarity_mx][1]
    return inverse_genres[similarity_id], similarity_value


# add fallback is results are empty
class ActionDiscoverMovie(Action):
    def name(self) -> Text:
        return "action_discover_movie"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        movie_or_tv = tracker.get_slot("movie_or_tv")
        if movie_or_tv is None:
            print("movie or tv not set")
            return []
        genre_ids = get_slot_ids(movie_or_tv)

        genre = tracker.get_slot("genre")
        if movie_or_tv == "movie":
            if genre is None:
                discover = tmdb.Discover()
                response = discover.movie()
            else:
                discover = tmdb.Discover()
                response = discover.movie(with_genres=genre_ids[genre])
        elif movie_or_tv == "tv show":
            if genre is None:
                discover = tmdb.Discover()
                response = discover.tv()
            else:
                discover = tmdb.Discover()
                response = discover.tv(with_genres=genre_ids[genre])
        # top 3 results
        if response["total_results"] == 0:
            evt = SlotSet("top_names", "")
            return [evt]
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
            return [evt, ent]


# # add fallback is results are empty
# class ActionCleanGenres(Action):
#     def name(self) -> Text:
#         return "action_clean_genres"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         evt = SlotSet("genre",None)
#         return [evt]


# add fallback is results are empty
class ActionGenresAvailable(Action):
    def name(self) -> Text:
        return "action_genres_available"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        movie_or_tv = tracker.get_slot("movie_or_tv")
        if movie_or_tv == None:
            print("movie or tv not set")
            return []
        genres = get_slot_ids(movie_or_tv)
        genres_available = list(genres.keys())
        genres_available[-1] = "and " + genres_available[-1]
        genres_available = ", ".join(genres_available)
        print(genres_available)
        evt = SlotSet("genres_available", genres_available)
        return [evt]


# lookup specific movie
class ActionLookupMovie(Action):
    def name(self) -> Text:
        return "action_lookup_movie"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # print('Hi')
        # state = tracker.current_state()
        # from pprint import pprint
        # pprint(state)
        return []


class CustomGenreValidation(Action):
    def name(self) -> Text:
        return "custom_genre_validation"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # print('Hi')
        # state = tracker.current_state()
        # from pprint import pprint
        # pprint(state)

        movie_or_tv = tracker.get_slot("movie_or_tv")
        if Levenshtein.jaro(movie_or_tv, "movie") > Levenshtein.jaro(
            movie_or_tv, "tv show"
        ):
            movie_or_tv = "movie"
        else:
            movie_or_tv = "tv show"
        evt_movie_or_tv = SlotSet("movie_or_tv", movie_or_tv)

        genre = tracker.get_slot("genre")

        if genre is None:
            evt_genre = SlotSet("genre", None)
            evt_validated = SlotSet("genre_validated", True)
            evt_suggested_genre = SlotSet("suggested_genre", None)
            return [evt_movie_or_tv, evt_genre, evt_validated, evt_suggested_genre]
        else:
            matched_genre, confidence = genre_matcher(genre, movie_or_tv)
            print(
                f"genre {genre} was matched to {matched_genre} with confidence {confidence}"
            )
            if confidence > 0.9:
                evt_genre = SlotSet("genre", matched_genre)
                evt_validated = SlotSet("genre_validated", True)
                evt_suggested_genre = SlotSet("suggested_genre", None)
                return [evt_movie_or_tv, evt_genre, evt_validated]
            elif confidence > 0.6:
                evt_genre = SlotSet("genre", genre)
                evt_validated = SlotSet("genre_validated", False)
                evt_suggested_genre = SlotSet("suggested_genre", matched_genre)
                return [evt_movie_or_tv, evt_genre, evt_validated, evt_suggested_genre]
            else:
                evt_genre = SlotSet("genre", genre)
                evt_validated = SlotSet("genre_validated", False)
                evt_suggested_genre = SlotSet("suggested_genre", None)
                return [evt_movie_or_tv, evt_genre, evt_validated, evt_suggested_genre]


class CustomGenreValidationConfirmation(Action):
    def name(self) -> Text:
        return "custom_genre_validation_confirmation"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # print('Hi')
        # state = tracker.current_state()
        # from pprint import pprint
        # pprint(state)

        movie_or_tv = tracker.get_slot("movie_or_tv")
        if Levenshtein.jaro(movie_or_tv, "movie") > Levenshtein.jaro(
            movie_or_tv, "tv show"
        ):
            movie_or_tv = "movie"
        else:
            movie_or_tv = "tv show"
        evt_movie_or_tv = SlotSet("movie_or_tv", movie_or_tv)

        genre = tracker.get_slot("genre")
        suggested_genre = tracker.get_slot("suggested_genre")
        print(f"genre {genre} was replaced with {suggested_genre}")
        evt_genre = SlotSet("genre", suggested_genre)
        evt_validated = SlotSet("genre_validated", True)
        evt_suggested_genre = SlotSet("suggested_genre", None)
        return [evt_movie_or_tv, evt_genre, evt_validated, evt_suggested_genre]


# from typing import Text, Any, Dict

# from rasa_sdk import Tracker, ValidationAction
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.types import DomainDict


# class ValidatePredefinedSlots(ValidationAction):

#     def validate_genre(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) ->   List[Dict[Text, Any]]:
#         """Validate genre value."""
#         print(f"slot_value {slot_value}")
#         movie_or_tv = tracker.get_slot('movie_or_tv')
#         if movie_or_tv == None:
#             print('movie or tv not set')
#             return {"genre": None}
#         # here i match to movie_or_tv
#         genre,confidence = genre_matcher(slot_value,movie_or_tv)
#         if confidence < 0.8:
#             print('confidence too low')
#             return {"genre": None}
#         print(f"was mapped to {genre} with confidence {confidence}")
#         return [{"genre": genre}]
#     def validate_movie_or_tv(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate movie or tv value."""
#         print(f"slot_value {slot_value}")
#         movie_or_tv = tracker.get_slot('movie_or_tv')
#         movie = Levenshtein.jaro(movie_or_tv,'movie')
#         tv_show = Levenshtein.jaro(movie_or_tv,'tv show')
#         if movie > tv_show:
#             movie_or_tv = 'movie'
#         else:
#             movie_or_tv = 'tv show'
#         print(f"was mapped to {movie_or_tv}")
#         return {"movie_or_tv": movie_or_tv}

# from typing import Text, List, Any, Dict

# from rasa_sdk import Tracker, FormValidationAction
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.types import DomainDict


# class ValidateGenreForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_discovery_form"

#     def validate_genre(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate genre value."""
#         # validation succeeded, capitalize the value of the "location" slot
#         movie_or_tv = tracker.get_slot('movie_or_tv')
#         if movie_or_tv == None:
#             print('movie or tv not set')
#             return {"genre": None}
#         print(f"slot_value {slot_value}")
#         genre,confidence = genre_matcher(slot_value,movie_or_tv)
#         print(f"was mapped to {genre} with confidence {confidence}")
#         # if genre is None:
#             # print("genre not found")
#             # dispatcher.utter_message(text="Sorry, I didn't understand that. Please try again.")
#             # return {"genre": None}
#         return {"genre": genre}
# class ValidateMovieTvForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_movie_tv_form"
#     def validate_movie_or_tv(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate movie or tv value."""
#         print(f"slot_value {slot_value}")
#         movie_or_tv = tracker.get_slot('movie_or_tv')
#         movie = Levenshtein.jaro(movie_or_tv,'movie')
#         tv_show = Levenshtein.jaro(movie_or_tv,'tv show')
#         if movie > tv_show:
#             movie_or_tv = 'movie'
#         else:
#             movie_or_tv = 'tv show'
#         print(f"was mapped to {movie_or_tv}")
#         return {"movie_or_tv": movie_or_tv}
