# function to get the slot ids
from typing import Dict, List
import Levenshtein
import requests
import tmdbsimple as tmdb

from enum_slots import MovieOrTv, Genre, Slots


class TMDBParser:
    """
    Class that parses the TMDB API in order to get the information needed for the bot as strings or json
    """

    # def __init__(self, api_key: str, request_timeout: int = 5, session : requests.Session = None):
    #     '''
    #     Class to instantiate the TMDB API
    #     :param api_key: the api key for the TMDB API
    #     :param request_timeout: the timeout for the requests
    #     :param session: the session to use for the requests
    #     '''
    #     tmdb.API_KEY = api_key
    #     tmdb.REQUESTS_TIMEOUT = request_timeout # seconds, for both connect and read
    #     tmdb.REQUESTS_SESSION = session
    def __init__(self):
        pass

    @staticmethod
    def list_to_string(self, list: List[str]) -> str:
        """
        method to convert a list to a string in a readable format with , and and as last item
        :param list: the list to convert
        :return: the string of the list
        """
        other = list[:-1]
        result = ", ".join(other)
        result += " and " + list[-1]
        return result

    @staticmethod
    def discover_genres(self, movie_or_tv: str) -> List[str]:
        """
        Method to get the genres available for either movies or tv shows
        :param movie_or_tv: either {MovieOrTv.movie.value} or {MovieOrTv.tv_show.value}
        :return: a list of the genres available
        """
        genres = self.get_slot_ids(movie_or_tv)
        genres_available = list(genres.keys())
        return genres_available

    @staticmethod
    def discover(self, movie_or_tv: str, genre: str) -> List[Dict]:
        """
        get the results for the movie or tv show based on the genre.
        :param movie_or_tv: either {MovieOrTv.movie.value} or {MovieOrTv.tv_show.value}
        :param genre: the genre of the movie or tv show
        :return: a list of the results
        """
        genre_ids = self.get_slot_ids(movie_or_tv)
        if movie_or_tv == MovieOrTv.movie.value:
            discover = tmdb.Discover()
            response = discover.movie(with_genres=genre_ids[genre])
        elif movie_or_tv == MovieOrTv.tv_show.value:
            discover = tmdb.Discover()
            response = discover.tv(with_genres=genre_ids[genre])
        else:
            raise ValueError(
                f"movie_or_tv must be either {MovieOrTv.movie.value} or {MovieOrTv.tv_show.value}"
            )
        return response
    @staticmethod
    def response_to_names
    @staticmethod
    def get_slot_ids(self, movie_or_tv: str) -> Dict:
        """
        method to get the slot ids for the genres or either movies or tv shows
        :param movie_or_tv: either 'movie' or 'tv'
        :return: a dictionary of the genres and their ids with the genre name as the key
        :raise ValueError: if movie_or_tv is not 'movie' or 'tv'
        """
        genre = tmdb.Genres()
        genres = dict()
        genres[Genre.popular.value] = None
        if movie_or_tv == MovieOrTv.movie.value:
            for item in genre.movie_list()["genres"]:
                genres[item["name"]] = str(item["id"])
        elif movie_or_tv == MovieOrTv.tv_show.value:
            for item in genre.tv_list()["genres"]:
                genres[item["name"]] = str(item["id"])
        else:
            raise ValueError(
                f"movie_or_tv must be either {MovieOrTv.movie.value} or {MovieOrTv.tv_show.value}"
            )
        return genres

    @staticmethod
    def genre_matcher(self, selected_genre: str, movie_or_tv: str):
        """
        method to match the selected genre to the genres in the TMDB API
        """
        print(selected_genre)
        selected_genre = selected_genre.lower()
        genres_og = self.get_slot_ids(movie_or_tv)
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
                        Levenshtein.jaro(selected_genre, word),
                        similarity[genre_lower][0],
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
