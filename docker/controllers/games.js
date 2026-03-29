const path = require('path');
const Game = require('../models/games');

exports.index = function (req, res) {
  res.sendFile(path.resolve('views/games.html'));
};

exports.create = function (req, res) {
  var newGame = new Game(req.body);
  console.log(req.body);
  newGame.save(function (err) {
    if (err) {
      res.status(400).send('Unable to save game to database');
    } else {
      res.redirect('/games/getgame');
    }
  });
};

exports.list = function (req, res) {
  Game.find({}).exec(function (err, games) {
    if (err) {
      return res.send(500, err);
    }
    res.render('getgame', { games: games });
  });
};
