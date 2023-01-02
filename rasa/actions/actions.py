# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

# tmdb api key
import tmdbsimple as tmdb
tmdb.API_KEY = 'c038a92e3fe9346f02feaf2d8ae2efab'

# 5 seconds timeout for requests to avoid blocking
tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read

class Action_discover_movie(Action):

    def name(self) -> Text:
        return "action_discover_movie"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # connect to tmdb api
        discover = tmdb.Discover()
        response = discover.movie()
        # top 3 results
        results = response['results'][:3]
        top_names = [result['title'] for result in results]
        dispatcher.utter_message(text="Hello World!")
        return []