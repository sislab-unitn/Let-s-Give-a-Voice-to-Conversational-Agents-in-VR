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

async function action_get_avaliable_genres(contextMap) {
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
  var genres_available = [];
  //console.log('results.genres: ', results.genres);
  results.genres.forEach((genre) => { genres_available.push( {name:genre.name,id:genre.id}) })
  //console.log('genres_available: ', genres_available);
  return genres_available;
}

const actions = {
  async validate_genres(contextMap) {
    var distance = require('jaro-winkler');
    const {genre} = contextMap;
    console.log('genre: ', genre[0].value);
    //genre = contextMap.genre = genre;
    if (typeof genre !== 'object') {
      console.log('processing error');
      return {context_map: contextMap};
    }
    var genre_valid = false;
    var corrected_genre = null;
    var results = await action_get_avaliable_genres(contextMap);
    //console.log('results: ', results);
    var genre_names = results.map((genre) => { return genre.name });
    //console.log('genre_names: ', genre_names);
    if (genre_names.includes(genre[0].value))
      genre_valid = true;
    else{
      genre_valid = false;
      // calculate distance between genre[0].value and each genre_name with a dictionary of genre_names
      //var g_distances = [];
      //genre_names.forEach((genre_name) => { g_distances.push(genre_name:distance(genre_name, genre[0].value)) });
      var g_distances = genre_names.map((genre_name) => { return [genre_name,distance(genre_name, genre[0].value)] });
      // sort by decreasing distance
      //console.log('g_distances: ', g_distances);
      var g_distances_sorted = g_distances.sort((a, b) => b[1] - a[1]);
      if (g_distances_sorted[0][1] > 0.7){
        genre_valid = true;
        contextMap.genre[0].value = g_distances_sorted[0][0];
      }
      console.log('g_distances_sorted: ', g_distances_sorted);
    }
    console.log('genre_valid: ', genre_valid);
    // var genre_name = genre[0].value;
    var genre_string = '';
    genre_names.forEach((genre_name) => { genre_string += genre_name + ', '})
    return {context_map: {...contextMap, genre_valid, genres_available:genre_string}};
  },
  async action_get_avaliable_genres(contextMap) {
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
    results.genres.forEach((genre) => { genres_available += genre.name + ', '})
    return {context_map: {...contextMap, genres_available}};
  },
  async action_get_popular_movies(contextMap) {
    console.log('action_get_popular_movies');
    //console.log('contextMap: ', contextMap); 
    const {movie_or_tv} = contextMap;
    //console.log('movie_or_tv: ', movie_or_tv);
    console.log('movie_or_tv: ', movie_or_tv[0].value);
    if (typeof movie_or_tv !== 'object') {
      console.log('processing error - movie_or_tv missing');
      return {context_map: contextMap};
    } 
    var results = null;
    var top_names = '';
    if (movie_or_tv[0].value === 'movie') {
      results = await moviedb.discoverMovie();
      results.results.slice(0, 3).forEach((movie) => { top_names += movie.title + ', ' })
    } else if (movie_or_tv[0].value === 'tv show') {
      results = await moviedb.discoverTv();
      results.results.slice(0, 3).forEach((movie) => { top_names += movie.name + ', ' })
    } else {
      console.log('processing error - movie_or_tv.value not valid');
    }
    
    return {context_map: {...contextMap, top_names}};
  },
  async action_get_movies(contextMap) {
    console.log('action_get_movies');
    const {movie_or_tv} = contextMap;
    //console.log('contextMap: ', contextMap);
    var genres_available = await action_get_avaliable_genres(contextMap);
    //console.log('genres_available: ', genres_available);
    var id = genres_available.find(genre => genre.name === contextMap.genre[0].value).id; 
    console.log('genre: ', contextMap.genre[0].value);
    console.log('id: ', id);
    var results = null;
    var top_names = '';
    if (movie_or_tv[0].value === 'movie') {
      results = await moviedb.discoverMovie({with_genres:id});
      results.results.slice(0, 3).forEach((movie) => { top_names += movie.title + ', ' })
    }
    else if (movie_or_tv[0].value === 'tv show') {
      results = await moviedb.discoverTv({with_genres:id});
      results.results.slice(0, 3).forEach((movie) => { top_names += movie.name + ', ' })
    } else {
      console.log('processing error - movie_or_tv.value not valid');
    }
    
    return {context_map: {...contextMap, top_names}};
  },
};

const {MovieDb} = require('moviedb-promise');
const moviedb = new MovieDb(accessTokenTmdb);
const client = new Wit({accessTokenWit,actions});
interactive(client);
