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
tmdb.API_KEY = 'c038a92e3fe9346f02feaf2d8ae2efab'
# 5 seconds timeout for requests to avoid blocking
tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read
def parse_data

# add fallback is results are empty
class ActionDiscoverMovie(Action):
    def get_slot_ids(self) -> Dict:
        genre = tmdb.Genres()
        genres =  {}
        for item in genre.movie_list()['genres']:
            genres[item['name']] = str(item['id'])
        return genres
    def name(self) -> Text:
        return "action_discover_movie"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
       
        genre = tracker.get_slot('genre')
        if genre==None:
            discover = tmdb.Discover()
            response = discover.movie()
        else:   
            genre = self.get_slot_ids()[genre]
            discover = tmdb.Discover()
            response = discover.movie(with_genres=genre)
        # top 3 results
        results = response['results'][:3]
        top_names = [result['title'] for result in results]
        top_names[-1] = "and " + top_names[-1]
        top_names = ", ".join(top_names)
        print(top_names)
        #dispatcher.utter_message(utter_message="utter_greet")
        #print("ww")
        evt = SlotSet("top_names",top_names)
        return [evt]


# add fallback is results are empty
class ActionGenresAvailable(Action):
    def get_slot_ids(self) -> Dict:
        genre = tmdb.Genres()
        genres =  {}
        for item in genre.movie_list()['genres']:
            genres[item['name']] = str(item['id'])
        return genres
    def name(self) -> Text:
        return "action_genres_available"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        genres = self.get_slot_ids()
        
        genres_available = list(genres.keys())
        genres_available[-1] = "and " + genres_available[-1]
        genres_available = ", ".join(genres_available)
        print(genres_available)
        evt = SlotSet("genres_available",genres_available)
        return [evt]


# from typing import Text, List, Any, Dict

# from rasa_sdk import Tracker, FormValidationAction
# from rasa_sdk.executor import CollectingDispatcher
# from rasa_sdk.types import DomainDict


# class ValidateGenreForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_genre_form"

#     @staticmethod
#     def genre_db() -> List[Text]:
#         """Database of supported genres"""
        
#         return ["caribbean", "chinese", "french"]

#     def validate_genre(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:
#         """Validate genre value."""

#         if slot_value.lower() in self.genre_db():
#             # validation succeeded, set the value of the "genre" slot to value
#             return {"genre": slot_value}
#         else:
#             # validation failed, set this slot to None so that the
#             # user will be asked for the slot again
#             return {"genre": None}