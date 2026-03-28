const mongoose = require('mongoose');

const MONGO_HOSTNAME = 'mongo';
const MONGO_PORT = '27017';
const MONGO_DB = 'sharkinfo';

const url = `mongodb://${MONGO_HOSTNAME}:${MONGO_PORT}/${MONGO_DB}`;

mongoose.connect(url, { useNewUrlParser: true });
