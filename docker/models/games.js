const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const Game = new Schema({
  name: { type: String, required: true },
  genre: { type: String, required: true },
});

module.exports = mongoose.model('Game', Game);
