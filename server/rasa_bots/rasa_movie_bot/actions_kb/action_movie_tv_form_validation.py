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


class ValidateMovieTvForm(FormValidationAction):
    def name(self) -> Text:
        return Actions.ValidateMovieTvForm.value

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
