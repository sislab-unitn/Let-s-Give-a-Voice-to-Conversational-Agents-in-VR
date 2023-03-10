import tmdbsimple as tmdb
import sys
import os
import Levenshtein
import requests

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config_parser import config_parser
from tmdb_parser import tmdbParser


# remove the first argument (the script name) and rasa init stuff
config = config_parser()
tmdb.API_KEY = config['server']['tmdb_API']

# 5 seconds timeout for requests to avoid blocking
tmdb.REQUESTS_TIMEOUT = 5  # seconds, for both connect and read
tmdb.REQUESTS_SESSION = requests.Session()
# complete a search to ensure that the API key is valid and the connection is working
__ = tmdb.Discover()

the_movie_db = tmdbParser()
