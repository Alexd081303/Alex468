Alex468





<img width="900" height="400" alt="project_vision_diagram" src="https://github.com/user-attachments/assets/911df427-5ee2-4938-9e48-87ead86019cb" />

# CSC 466 — Docker + MongoDB Video Game App

A containerized Node.js + MongoDB web application where users can submit
their favorite video games and genres, which are stored in MongoDB and
displayed back in the browser.

Developed by **Alexander Dimichele**

---

## Folder Structure
```
csc466-docker-mongo/
├── docker-compose.yml            # Defines and links the two services
├── docker/                       # Node.js application container
│   ├── Dockerfile                # Build instructions for the web service
│   ├── package.json              # Node dependencies
│   ├── app.js                    # Express app entry point
│   ├── db.js                     # MongoDB connection setup
│   ├── controllers/
│   │   └── sharks.js             # Handles request logic (index, create, list)
│   ├── models/
│   │   └── games.js              # Mongoose schema and model definition
│   ├── routes/
│   │   └── sharks.js             # Game routes (GET, POST)
│   └── views/
│       ├── index.html            # Landing page
│       ├── games.html            # Game input form
│       ├── getgame.html          # Results page (EJS template)
│       └── css/
│           └── styles.css        # Stylesheet
```

---

## Build Process

### Base Image Choice

The Node.js service uses `node:alpine` as its base image. Alpine Linux is a
minimal Linux distribution that produces significantly smaller images compared
to standard Debian-based Node images — roughly 50MB versus 350MB+. This makes
builds faster, reduces storage usage on CloudLab, and limits the attack surface
of the container. Since the application only requires Node.js and npm with no
system-level dependencies, Alpine is the right fit.

The MongoDB service uses the official `mongo:6` image directly without a custom
Dockerfile, since no modifications to the database layer are needed. Version 6
is a stable long-term release with strong Mongoose compatibility.

### Dockerfile Line-by-Line
```dockerfile
FROM node:alpine
```
Pulls the official Node.js image built on Alpine Linux as the starting point.
This gives us a working Node and npm environment in a minimal footprint,
keeping the final image small and fast to build.
```dockerfile
RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app
```
Creates the application directory inside the container and sets ownership to
the built-in `node` user. Running as a non-root user is a security best
practice — if the container were ever compromised, the attacker would not
have root access to the host system.
```dockerfile
WORKDIR /home/node/app
```
Sets the working directory for all subsequent instructions. Any `COPY`, `RUN`,
or `CMD` commands will execute relative to this path, keeping paths clean and
avoiding ambiguity.
```dockerfile
COPY package*.json ./
```
Copies only the package files before copying the rest of the source code. This
is a deliberate Docker layer caching strategy: since dependencies change far
less often than application code, Docker can reuse the cached `npm install`
layer on rebuilds as long as `package.json` has not changed, making iterative
development builds significantly faster.
```dockerfile
RUN npm install
```
Installs all Node.js dependencies defined in `package.json` — specifically
Express (web framework), Mongoose (MongoDB ODM), and EJS (HTML templating
engine). This runs inside the container at build time so the final image
includes all required packages without needing an internet connection at
runtime.
```dockerfile
COPY --chown=node:node . .
```
Copies the rest of the application source code into the container. The
`--chown` flag ensures all copied files are owned by the `node` user,
maintaining the principle of least privilege consistently across the
container filesystem.
```dockerfile
USER node
```
Switches the active user from root to the `node` user for all subsequent
instructions and at runtime. This ensures the Node.js process itself runs
without elevated privileges, reducing risk if the application is exploited.
```dockerfile
EXPOSE 8080
```
Documents that the container listens on port 8080 at runtime. This does not
actually publish the port to the host — that is handled by the `ports` mapping
in `docker-compose.yml`. It serves as documentation for developers and is used
by Docker's internal networking layer.
```dockerfile
CMD ["node", "app.js"]
```
Defines the default command to run when the container starts. The exec form
(JSON array) is used rather than shell form, which ensures Node.js runs as
PID 1 directly. This means the process properly receives OS signals like
SIGTERM, enabling graceful shutdown when `docker compose down` is called.

---

## Networking

### Overview

The two services — `app` (Node.js) and `mongo` (MongoDB) — communicate over
Docker's default **bridge network**, which Docker Compose automatically creates
when the stack is started with `docker compose up`. No manual network
configuration is required.

### Bridge Network

A bridge network is a private internal network created on the host machine.
Containers attached to the same bridge network can reach each other directly
using their service names as hostnames, while remaining isolated from
containers on other networks and from the public internet unless ports are
explicitly published.

Docker Compose automatically connects all services defined in
`docker-compose.yml` to a shared bridge network named after the project
directory — in this case `csc466-docker-mongo_default`. Both the `app` and
`mongo` containers are attached to this network automatically at startup.

### DNS Resolution by Container Name

Docker provides automatic DNS resolution within the bridge network. Each
service name in `docker-compose.yml` becomes a resolvable hostname for all
other containers on the same network. This is why the database connection in
`db.js` uses `mongo` as the hostname rather than an IP address:
```javascript
const MONGO_HOSTNAME = 'mongo';
const url = `mongodb://${MONGO_HOSTNAME}:27017/sharkinfo`;
```

When the Node.js container executes this connection string, Docker's internal
DNS resolver translates `mongo` to the current IP address of the MongoDB
container automatically. Hardcoding IP addresses would break every time the
stack is restarted, since Docker assigns container IPs dynamically. Using
service names makes the configuration stable and portable.

### Port Publishing

The `docker-compose.yml` maps port `8080` on the CloudLab host to port `8080`
inside the `app` container, making the web application reachable from a browser
using the CloudLab node's public IP address:
```yaml
ports:
  - "8080:8080"
```

The MongoDB port `27017` is intentionally not published to the host. This means
the database is only reachable from within the internal bridge network — other
containers can connect to it, but external traffic cannot. This follows standard
security practice by keeping the database layer private and only exposing the
web layer publicly.

### depends_on
```yaml
depends_on:
  - mongo
```

This directive tells Docker Compose to start the `mongo` container before the
`app` container. Without this, the Node.js app could attempt its MongoDB
connection before the database is ready to accept it, causing a startup error.

---
