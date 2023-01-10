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
tmdb.API_KEY = 'c038a92e3fe9346f02feaf2d8ae2efab'
# 5 seconds timeout for requests to avoid blocking
tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read

# add fallback is results are empty
class ActionDiscoverMovie(Action):
    def get_slot_ids(self,movie_or_tv) -> Dict:
        genre = tmdb.Genres()
        genres =  {}
        if movie_or_tv == 'movie':
            for item in genre.movie_list()['genres']:
                genres[item['name'].lower()] = str(item['id'])
        else:
            for item in genre.tv_list()['genres']:
                genres[item['name'].lower()] = str(item['id'])
        return genres
    def genre_matcher(self,selected_genre,movie_or_tv):
        genres = self.get_slot_ids(movie_or_tv)
        similarity = {}
        for genre in genres:
            for word in genre.split():
                try:
                    similarity[genre] += Levenshtein.jaro(selected_genre,word)
                except KeyError:
                    similarity[genre] = Levenshtein.jaro(selected_genre,word)
        # max similarity
        similarity = max(similarity, key=similarity.get)
        return similarity
    def name(self) -> Text:
        return "action_discover_movie"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        movie_or_tv = tracker.get_slot('movie_or_tv')
        if movie_or_tv == None:
            print('movie or tv not set')
            return []
        genre_ids = self.get_slot_ids(movie_or_tv)
        try:
            genre = tracker.get_slot('genre').lower()
        except AttributeError:
            genre = tracker.get_slot('genre')
        if movie_or_tv == 'movie':
            if genre==None:
                discover = tmdb.Discover()
                response = discover.movie()
            else:   
                genre = self.genre_matcher(genre,movie_or_tv)
                discover = tmdb.Discover()
                response = discover.movie(with_genres=genre_ids[genre])
        elif movie_or_tv == 'tv show':
            if genre==None:
                discover = tmdb.Discover()
                response = discover.tv()
            else:   
                genre = self.genre_matcher(genre,movie_or_tv)
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
            return [evt]


# add fallback is results are empty
class ActionCleanGenres(Action):
    def name(self) -> Text:
        return "action_clean_genres"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        evt = SlotSet("genre",None)
        return [evt]


# add fallback is results are empty
class ActionGenresAvailable(Action):
    def get_slot_ids(self,movie_or_tv) -> Dict:
        genre = tmdb.Genres()
        genres =  {}
        if movie_or_tv == 'movie':
            for item in genre.movie_list()['genres']:
                genres[item['name']] = str(item['id'])
        else:
            for item in genre.tv_list()['genres']:
                genres[item['name']] = str(item['id'])
        return genres
    def name(self) -> Text:
        return "action_genres_available"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        movie_or_tv = tracker.get_slot('movie_or_tv')
        if movie_or_tv == None:
            print('movie or tv not set')
            return []
        genres = self.get_slot_ids(movie_or_tv)
        genres_available = list(genres.keys())
        genres_available[-1] = "and " + genres_available[-1]
        genres_available = ", ".join(genres_available)
        print(genres_available)
        evt = SlotSet("genres_available",genres_available)
        return [evt]

# lookup specific movie
class ActionLookupMovie(Action):
    def name(self) -> Text:
        return "action_lookup_movie"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print('Hi')
        dispatcher.utter_message(utter_message="utter_greet")
  
  
from typing import Text, Any, Dict

from rasa_sdk import Tracker, ValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ValidatePredefinedSlots(ValidationAction):
    
    def get_slot_ids(self,movie_or_tv) -> Dict:
        genre = tmdb.Genres()
        genres =  {}
        if movie_or_tv == 'movie':
            for item in genre.movie_list()['genres']:
                genres[item['name']] = str(item['id'])
        else:
            for item in genre.tv_list()['genres']:
                genres[item['name']] = str(item['id'])
        return genres
    def genre_matcher(self,selected_genre,movie_or_tv):
        selected_genre = selected_genre.lower()
        genres_og = self.get_slot_ids(movie_or_tv)
        inverse_genres = {v: k for k, v in genres_og.items()}
        genres = {}
        for key,item in genres_og.items():
            genres[key.lower()] = item
        similarity = {}
        for genre in genres:
            for word in genre.split():
                try:
                    if selected_genre == word:
                        return inverse_genres[genres[genre]]
                    similarity[genre][0] += Levenshtein.jaro(selected_genre,word)
                    
                except KeyError:
                    similarity[genre] = [Levenshtein.jaro(selected_genre,word),genres[genre]]
        # max similarity
        similarity_mx = max(similarity, key = lambda x: similarity[x][0])
        similarity_id = similarity[similarity_mx][1]
        return inverse_genres[similarity_id]
    def validate_genre(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate genre value."""
        print(f"slot_value {slot_value}")
        movie_or_tv = tracker.get_slot('movie_or_tv')
        if movie_or_tv == None:
            print('movie or tv not set')
            return {"genre": None}
        genre = self.genre_matcher(slot_value,movie_or_tv)
        print(f"was mapped to {genre}")
        return {"genre": genre}
    def validate_movie_or_tv(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate movie or tv value."""
        print(f"slot_value {slot_value}")
        movie_or_tv = tracker.get_slot('movie_or_tv')
        movie = Levenshtein.jaro(movie_or_tv,'movie')
        tv_show = Levenshtein.jaro(movie_or_tv,'tv show')
        if movie > tv_show:
            movie_or_tv = 'movie'
        else:
            movie_or_tv = 'tv show'
        print(f"was mapped to {movie_or_tv}")
        return {"movie_or_tv": movie_or_tv}
       
from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


class ValidateGenreForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_discovery_form"
    
    def get_slot_ids(self,movie_or_tv) -> Dict:
        genre = tmdb.Genres()
        genres =  {}
        if movie_or_tv == 'movie':
            for item in genre.movie_list()['genres']:
                genres[item['name'].lower()] = str(item['id']).lower()
        else:
            for item in genre.tv_list()['genres']:
                genres[item['name'].lower()] = str(item['id']).lower()
        return genres
    def genre_matcher(self,selected_genre,movie_or_tv):
        selected_genre = selected_genre.lower()
        genres_og = self.get_slot_ids(movie_or_tv)
        inverse_genres = {v: k for k, v in genres_og.items()}
        genres = {}
        for key,item in genres_og.items():
            genres[key.lower()] = item
        similarity = {}
        for genre in genres:
            for word in genre.split():
                try:
                    if selected_genre == word:
                        return inverse_genres[genres[genre]]
                    similarity[genre][0] += Levenshtein.jaro(selected_genre,word)
                    
                except KeyError:
                    similarity[genre] = [Levenshtein.jaro(selected_genre,word),genres[genre]]
        # max similarity
        similarity_mx = max(similarity, key = lambda x: similarity[x][0])
        # if similarity_mx < 0.5:
        #     return None
        similarity_id = similarity[similarity_mx][1]
        return inverse_genres[similarity_id]
    def validate_genre(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate genre value."""
        # validation succeeded, capitalize the value of the "location" slot
        movie_or_tv = tracker.get_slot('movie_or_tv')
        if movie_or_tv == None:
            print('movie or tv not set')
            return {"genre": None}
        print(f"slot_value {slot_value}")
        genre = self.genre_matcher(slot_value,movie_or_tv)
        print(f"was mapped to {genre}")
        # if genre is None:
            # print("genre not found")
            # dispatcher.utter_message(text="Sorry, I didn't understand that. Please try again.")
            # return {"genre": None}
        return {"genre": genre}
class ValidateMovieTvForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_movie_tv_form"
    def validate_movie_or_tv(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate movie or tv value."""
        print(f"slot_value {slot_value}")
        movie_or_tv = tracker.get_slot('movie_or_tv')
        movie = Levenshtein.jaro(movie_or_tv,'movie')
        tv_show = Levenshtein.jaro(movie_or_tv,'tv show')
        if movie > tv_show:
            movie_or_tv = 'movie'
        else:
            movie_or_tv = 'tv show'
        print(f"was mapped to {movie_or_tv}")
        return {"movie_or_tv": movie_or_tv}