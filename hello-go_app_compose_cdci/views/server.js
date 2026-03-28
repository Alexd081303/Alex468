const express = require('express');
const mongoose = require('mongoose');

const app = express();

// MongoDB connection (service name from docker-compose)
mongoose.connect('mongodb://mongo:27017/sharks');

const Shark = mongoose.model('Shark', {
  name: String
});

app.set('view engine', 'ejs');

app.get('/', async (req, res) => {
  const sharks = await Shark.find();

  res.render('index', { sharks });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
