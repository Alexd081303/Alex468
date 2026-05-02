const mongoose = require('mongoose');

const MONGO_HOSTNAME = process.env.MONGO_HOSTNAME || 'mongo';
const MONGO_PORT = process.env.MONGO_PORT || '27017';
const MONGO_DB = process.env.MONGO_DB || 'sharkinfo';

const url = `mongodb://${MONGO_HOSTNAME}:${MONGO_PORT}/${MONGO_DB}`;

const connectWithRetry = () => {
  mongoose.connect(url, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('MongoDB connected successfully'))
    .catch(err => {
      console.error('MongoDB connection error — retrying in 5s:', err.message);
      setTimeout(connectWithRetry, 5000);
    });
};

connectWithRetry();
