
Copy

const mongoose = require('mongoose');
 
const MONGO_HOSTNAME = process.env.MONGO_HOSTNAME || 'mongo';
const MONGO_PORT = process.env.MONGO_PORT || '27017';
const MONGO_DB = process.env.MONGO_DB || 'sharkinfo';
 
const url = `mongodb://${MONGO_HOSTNAME}:${MONGO_PORT}/${MONGO_DB}`;
 
mongoose.connect(url, { useNewUrlParser: true })
  .then(() => console.log('MongoDB connected successfully'))
  .catch(err => console.error('MongoDB connection error:', err));
 
