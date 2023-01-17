# Conversational Agent for movies

This page contains a repo with a simple conversational agent. The conversational agent recommends movies and tv shows, with options to choose a genre.
There are two implementations, one in Rasa and the other using Wit.

The conversational agent retrieves data from [tmdb](https://www.themoviedb.org/) with their free to use API. Note that is necessary to have an account in order to get the required token that allows API requests. Check [here](https://www.themoviedb.org/faq/account) in order to get an account and generate a token

For now it is possible to:
- Ask for movie or tv show suggestion
- Recommendation by either popularity or specifying a genre
- Ask what genres are available for either movie or tv show

The model tries to handle different paths and apply error correction if necessary. There are some intrisic differences for the answers of the two implementations, rasa and wit, because of the different underlying models

## Rasa
This implementation uses a simple almost standard NLU pipeline with some stories. It uses a python backend to handle the custom actions to connect to the movie database. It uses [tmdbsimple](https://github.com/celiao/tmdbsimple/ ) as python wrapper for the tmdb API
### requirements

```
rasa
tmdbsimple # python wrapper of tmdb API
levenshtein # for string matching when genre has typos
```

It is possible to install `tmdbsimple` and  `levenshtein` using 
```
pip install tmdbsimple
pip install python-Levenshtein
```
for rasa refer to [rasa doc](https://rasa.com/docs/rasa/installation/environment-set-up/)
### Train and Usage

to train the model, enter the subfolder `rasa` then type

```
rasa train
```

then before using the model, it is necessary to start the action server by running on a separate terminal on the same `rasa` subfolder
```
rasa run actions
```

finally use the model by running on a terminal open on the subfolder `rasa`

```
rasa shell
```
## Wit

The Wit model uses a hidden pipeline from meta. The link to the online model is [here](). A javascript script runs the wrapper required to take the input and outputs from the online model using a node.js wrapper for the Wit API [here](https://github.com/wit-ai/node-wit). 

The conversational agent takes inputs locally, submits to the Wit online server and then receives the result. It also runs a javascript wrapper for the tmdb API found at [moviedb-promise](https://github.com/grantholle/moviedb-promise)

### requirements
```
nodejs
node-wit # wit wrapper in node
jaro-winkler # jaro winkler distance for string matching
moviedb-promise # tmdb API wrapper
```
Enter the node-wit subfolder and run to install required packages

```
npm install --save node-wit
npm install jaro-winkler
npm install moviedb-promise
```


### Train and Usage

Because the model is online, there is no need to train

To run
```
node examples/basic.js <wit-server-token> <tmdb-token>
```

## Credits

Michele Yin

- https://rasa.com/ for the rasa framework
- https://wit.ai/ for the wit framework
- https://www.themoviedb.org/ as backend for API requests
- https://github.com/celiao/tmdbsimple/ as python wrapper for TMDB
- https://github.com/jordanthomas/jaro-winkler node jaro-winkler distance
- https://github.com/grantholle/moviedb-promise node js wrapper fpr TMDB
- https://github.com/wit-ai/node-wit node js wrapper for Wit
- https://github.com/maxbachmann/python-Levenshtein for python levenhstein