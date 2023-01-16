/**
 * Copyright (c) Meta Platforms, Inc. and its affiliates. All Rights Reserved.
 */

'use strict';

let Wit = null;
let interactive = null;
try {
  // if running from repo
  Wit = require('../').Wit;
  interactive = require('../').interactive;
} catch (e) {
  Wit = require('node-wit').Wit;
  interactive = require('node-wit').interactive;
}


const accessTokenWit = (() => {
  if (process.argv.length !== 4) {
    console.log('usage: node examples/basic.js <wit-access-token> <tmdb-access-token>');
    process.exit(1);
  }
  return process.argv[2];
})();
const accessTokenTmdb = (() => {
  if (process.argv.length !== 4) {
    console.log('usage: node examples/basic.js <wit-access-token> <tmdb-access-token>');
    process.exit(1);
  }
  return process.argv[3];
})();
console.log('accessTokenWit: ', accessTokenWit);
console.log('accessTokenTmdb: ', accessTokenTmdb);

async function get_avaliable_genres(contextMap) {
  const {movie_or_tv} = contextMap;
  console.log('movie_or_tv: ', movie_or_tv[0].value);
  if (typeof movie_or_tv !== 'object') {
    console.log('processing error - movie_or_tv missing');
    return {context_map: contextMap};
  } 
  var results = null;
  if (movie_or_tv[0].value === 'movie') {
    results = await moviedb.genreMovieList();
  } else if (movie_or_tv[0].value === 'tv show') {
    results = await moviedb.genreTvList();
  } else {
    console.log('processing error - movie_or_tv.value not valid');
  }
  var genres_available = '';
  // console.log('results.genres: ', results.genres);
  genres_available = results.genres.forEach((genre) => { genres_available += genre.name + ', '})
  return genres_available;
}

const actions = {
  validate_genres(contextMap) {
    const {genre} = contextMap;
    contextMap.genre = genre;
    if (typeof genre !== 'object') {
      console.log('processing error');
      return {context_map: contextMap};
    }
    contextMap.genre_valid = true;
    return {context_map: contextMap};
  },
  async action_get_popular_movies(contextMap) {
    console.log('action_get_popular_movies');
    console.log('contextMap: ', contextMap);  
    const results = await moviedb.discoverMovie();
    var top_names = '';
    results.results.slice(0, 3).forEach((movie) => { top_names += movie.title + ', ' })
    return {context_map: {...contextMap, top_names}};
  },
  async action_get_movies(contextMap) {
    console.log('action_get_movies');
    console.log('contextMap: ', contextMap);  
    var genres_available = get_avaliable_genres(contextMap)
    console.log('genres_available: ', genres_available);
    const results = await moviedb.discoverMovie({with_genres:37});
    var top_names = '';
    results.results.slice(0, 3).forEach((movie) => { top_names += movie.title + ', ' })
    return {context_map: {...contextMap, top_names}};
  },
};

const {MovieDb} = require('moviedb-promise');
const moviedb = new MovieDb(accessTokenTmdb);
const client = new Wit({accessTokenWit,actions});
interactive(client);
