from enum import Enum


class Slots(Enum):
    movie_or_tv = "movie_or_tv"
    genre = "genre"
    top_results = "top_results"
    genres_available = "genres_available"


class MovieOrTv(Enum):
    movie = "movie"
    tv_show = "tv show"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

    def __hash__(self):
        return hash(self.value)


class Genre(Enum):
    action = "Action"
    adventure = "Adventure"
    animation = "Animation"
    comedy = "Comedy"
    crime = "Crime"
    documentary = "Documentary"
    drama = "Drama"
    family = "Family"
    fantasy = "Fantasy"
    history = "History"
    horror = "Horror"
    music = "Music"
    mystery = "Mystery"
    romance = "Romance"
    science_fiction = "Science Fiction"
    tv_movie = "TV Movie"
    thriller = "Thriller"
    war = "War"
    western = "Western"
    action_adventure = "Action & Adventure"
    kids = "Kids"
    news = "News"
    reality = "Reality"
    sci_fi_fantasy = "Sci-Fi & Fantasy"
    soap = "Soap"
    talk = "Talk"
    war_politics = "War & Politics"
    popular = "Popular"
