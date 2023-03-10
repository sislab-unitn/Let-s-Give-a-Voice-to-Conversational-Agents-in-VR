

# function to get the slot ids
from typing import Dict
import tmdbsimple as tmdb

class tmdbParser:
    def __init__(self):
        pass
def get_slot_ids(movie_or_tv) -> Dict:
        genre = tmdb.Genres()
        genres =  {}
        if movie_or_tv == 'movie':
            for item in genre.movie_list()['genres']:
                genres[item['name']] = str(item['id'])
        else:
            for item in genre.tv_list()['genres']:
                genres[item['name']] = str(item['id'])
        return genres

def genre_matcher(selected_genre,movie_or_tv):
    print(selected_genre)
    selected_genre = selected_genre.lower()
    genres_og = get_slot_ids(movie_or_tv)
    inverse_genres = {v: k for k, v in genres_og.items()}
    genres_lower = {}
    for key,item in genres_og.items():
        genres_lower[key.lower()] = item
    similarity = {}
    for genre_lower in genres_lower:
        for word in genre_lower.split():
            try:
                if selected_genre == word:
                    return inverse_genres[genres_lower[genre_lower]],1
                similarity[genre_lower][0] = max(Levenshtein.jaro(selected_genre,word),similarity[genre_lower][0])
            except KeyError:
                similarity[genre_lower] = [Levenshtein.jaro(selected_genre,word),genres_lower[genre_lower]]
    # max similarity
    similarity_mx = max(similarity, key = lambda x: similarity[x][0])
    inverse_similarity = {v[0]: k for k, v in similarity.items()}
    similarity_value = max(inverse_similarity, key = lambda x: x)
    similarity_id = similarity[similarity_mx][1]
    return inverse_genres[similarity_id],similarity_value