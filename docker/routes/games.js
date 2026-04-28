const express = require('express');
const router = express.Router();
const game = require('../controllers/games');

router.get('/', function (req, res) {
  game.index(req, res);
});

router.post('/addgame', function (req, res) {
  game.create(req, res);
});

router.get('/getgame', function (req, res) {
  game.list(req, res);
});

module.exports = router;
