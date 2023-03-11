from typing import Text, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

import Levenshtein

from .enum_slots import MovieOrTv, Genre, Slots
from .enum_actions import Actions


class ValidateMovieTvForm(FormValidationAction):
    def name(self) -> Text:
        return Actions.ValidateMovieTvForm.value

    def validate_movie_tv(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate movie or tv value."""
        print(f"slot_value {slot_value}")
        movie_or_tv = tracker.get_slot(MovieOrTv.movie.value)
        movie = Levenshtein.jaro(movie_or_tv, MovieOrTv.movie.value)
        tv_show = Levenshtein.jaro(movie_or_tv, MovieOrTv.tv_show.value)
        if movie > tv_show:
            movie_or_tv = MovieOrTv.movie.value
        else:
            movie_or_tv = MovieOrTv.tv_show.value
        print(f"was mapped to {movie_or_tv}")
        return {Slots.movie_or_tv.value: movie_or_tv}
