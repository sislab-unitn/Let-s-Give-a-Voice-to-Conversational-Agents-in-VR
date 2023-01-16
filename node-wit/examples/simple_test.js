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
const actions = {
  action_get_popular_movies(contextMap) {
    const {order} = contextMap;
    if (typeof order !== 'object') {
      console.log('processing error');
      return {context_map: contextMap};
    }

    return {context_map: {...contextMap, pizze_number, order_number}};
  },
};
const {MovieDb} = require('moviedb-promise');
const moviedb = new MovieDb(accessTokenTmdb);
const client = new Wit({accessTokenWit,actions});
interactive(client);
