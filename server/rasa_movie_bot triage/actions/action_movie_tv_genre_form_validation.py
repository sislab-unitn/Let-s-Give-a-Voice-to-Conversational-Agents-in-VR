import os
import sys
from typing import Any, Dict, Text

import Levenshtein
from rasa_sdk import FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

# add this folder to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from enum_actions import Actions
from enum_slots import Genre, MovieOrTv, Slots
from tmdb_parser import TMDBParser


class ValidateMovieTvGenreForm(FormValidationAction):
    def name(self) -> Text:
        return Actions.ValidateMovieTvGenreForm.value

    def validate_movie_or_tv(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate movie or tv value."""
        print(f"slot_value {slot_value}")
        movie_or_tv = tracker.get_slot(Slots.movie_or_tv.value)
        movie = Levenshtein.jaro(movie_or_tv, MovieOrTv.movie.value)
        tv_show = Levenshtein.jaro(movie_or_tv, MovieOrTv.tv_show.value)
        if movie > tv_show:
            movie_or_tv = MovieOrTv.movie.value
        else:
            movie_or_tv = MovieOrTv.tv_show.value
        print(f"was mapped to {movie_or_tv}")
        return {Slots.movie_or_tv.value: movie_or_tv}

    def validate_genre(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate genre value."""
        print(f"slot_value {slot_value}")
        movie_or_tv = tracker.get_slot(Slots.movie_or_tv.value)
        # here i match to movie_or_tv
        genre, confidence = TMDBParser.genre_matcher(slot_value, movie_or_tv)
        if confidence < 0.8:
            print("confidence too low")
            genres_available = TMDBParser.discover_genres(movie_or_tv)
            # convert to string
            genres_available = TMDBParser.list_to_string(genres_available)
            dispatcher.utter_message(text=f"I'm sorry, I didn't understand that. {slot_value} is not a valid genre for {movie_or_tv}. Valid genres are: {genres_available}.")
            return {Slots.genre.value: None}
        print(f"was mapped to {genre} with confidence {confidence}")
        return {Slots.genre.value: genre}
