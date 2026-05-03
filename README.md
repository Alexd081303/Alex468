Alex468





<img width="900" height="400" alt="project_vision_diagram" src="https://github.com/user-attachments/assets/911df427-5ee2-4938-9e48-87ead86019cb" />

# CSC 466 — Docker + MongoDB Video Game App

A fully containerized, multi-service web application where users can submit their favorite video games and genres. Data is stored in MongoDB and displayed back in the browser. A Python Flask REST API and a background worker service round out a three-tier architecture deployed on CloudLab.
Developed by Alexander Dimichele

Table of Contents

System Architecture
Folder Structure
Container Design & Base Images
Dockerfile Walkthrough
Networking
CloudLab Deployment
Automation Scripts
cgroups & Namespaces
Learning Outcomes


1. System Architecture
                        ┌──────────────────────────────────┐
                        │         Docker Bridge Network     │
                        │           app-network             │
                        │                                   │
  Browser ──── :8080 ──►│  app (Node.js/Express)            │
                        │       │           │               │
  curl    ──── :5000 ──►│  api (Flask)      │               │
                        │       │           │               │
                        │  worker (Python)──┘               │
                        │       │                           │
                        │  mongo (MongoDB 6) ◄──────────────┘
                        │       │
                        │  [mongo-data volume]
                        └──────────────────────────────────┘
The system consists of four services:
app — A Node.js/Express web server that renders HTML views using EJS. It accepts game submissions from the browser, writes them to MongoDB, and displays the full game list. Exposed on port 8080.
api — A Python Flask REST API that reads game data from MongoDB and exposes it as JSON. It provides a /api/games endpoint for the full game list and /api/games/stats for genre breakdowns. Exposed on port 5000.
worker — A Python background service that polls the API every 30 seconds and logs game statistics to stdout. It demonstrates persistent inter-service communication over the internal network without any exposed ports.
mongo — The official MongoDB 6 image used as a shared data store. Its data is persisted to a named Docker volume (mongo-data) so game entries survive container restarts. Its port is intentionally not published to the host.

2. Folder Structure
csc466-docker-mongo/
├── docker-compose.yml            # Defines all four services and the bridge network
├── profile_docker.py             # CloudLab RSpec profile — provisions and auto-deploys
├── cloudlab/
│   └── setup.sh                  # Manual Docker install script for CloudLab nodes
├── scripts/
│   ├── deploy.sh                 # Clone repo and bring stack up
│   └── network_test.sh           # Verify inter-container connectivity
├── docker/                       # Node.js web app container
│   ├── Dockerfile
│   ├── package.json
│   ├── app.js                    # Express entry point
│   ├── db.js                     # MongoDB connection with retry logic
│   ├── controllers/
│   │   └── games.js
│   ├── models/
│   │   └── games.js              # Mongoose schema
│   ├── routes/
│   │   └── games.js
│   └── views/
│       ├── index.html
│       ├── games.html
│       ├── getgame.html          # EJS template
│       └── css/
│           └── styles.css
├── api/                          # Python Flask REST API container
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── worker/                       # Python background worker container
    ├── Dockerfile
    ├── requirements.txt
    └── worker.py

3. Container Design & Base Images
ServiceBase ImageReasonappnode:alpineMinimal Node.js image (~50 MB vs 350 MB+ for Debian). No system-level dependencies needed beyond Node and npm.apipython:3.11-slimSlim Debian variant gives access to pip and the full Python standard library while keeping image size down.workerpython:3.11-slimSame reasoning as the API — lightweight and compatible with the requests library.mongomongo:6Official image; version 6 is a stable long-term release with strong Mongoose compatibility. No custom Dockerfile needed.
Alpine Linux is chosen for the Node.js service because it produces significantly smaller images. Smaller images pull faster on CloudLab, use less disk, and have a smaller attack surface. The Python services use python:3.11-slim rather than Alpine because some pip packages require C build tooling that is awkward to install on Alpine, and slim already provides a good size/compatibility tradeoff.

4. Dockerfile Walkthrough
Node.js App (docker/Dockerfile)
dockerfileFROM node:alpine
Pulls the official Node.js image on Alpine Linux — minimal footprint, fast build.
dockerfileRUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app
Creates the app directory and hands ownership to the built-in node user. Running as non-root is a security best practice — a compromised container does not gain root on the host.
dockerfileWORKDIR /home/node/app
Sets the working directory for all subsequent COPY, RUN, and CMD instructions.
dockerfileCOPY package*.json ./
RUN npm install
Copies only the package files before the source code. This exploits Docker's layer cache: as long as package.json has not changed, the npm install layer is reused on every rebuild, making iterative development significantly faster.
dockerfileCOPY --chown=node:node . .
Copies the application source. The --chown flag ensures all files are owned by node, maintaining least privilege throughout the container filesystem.
dockerfileUSER node
EXPOSE 8080
CMD ["node", "app.js"]
Switches to the unprivileged node user at runtime. EXPOSE documents the port. The exec-form CMD ensures Node runs as PID 1 and correctly receives SIGTERM signals during docker compose down, enabling graceful shutdown.
Python API & Worker (api/Dockerfile, worker/Dockerfile)
dockerfileFROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
The same layer-caching strategy applies: copying requirements.txt first means pip dependencies are only reinstalled when that file changes, not on every source code edit. --no-cache-dir avoids storing the pip download cache inside the image, keeping the final layer smaller.

5. Networking
Bridge Network
Docker Compose automatically creates a named bridge network (app-network) for all services. A bridge network is a private internal network on the host — containers on it can reach each other directly using service names as hostnames, while remaining isolated from the public internet unless ports are explicitly published.
DNS Resolution
Docker provides automatic DNS resolution within the bridge network. Each service name in docker-compose.yml becomes a resolvable hostname. This is why the MongoDB connection in db.js uses 'mongo' as the hostname rather than an IP address:
javascriptconst url = `mongodb://${MONGO_HOSTNAME}:${MONGO_PORT}/${MONGO_DB}`;
// MONGO_HOSTNAME defaults to 'mongo' — resolved by Docker's internal DNS
Hardcoding IP addresses would break on every stack restart, since Docker assigns container IPs dynamically. Service-name DNS is stable and portable across any Docker host.
The same principle applies to the worker, which calls http://api:5000/health to reach the Flask service — Docker DNS resolves api to the current IP of the API container automatically.
Port Publishing
PortPublished to HostPurpose8080✅ YesWeb app accessible from browser5000✅ YesAPI accessible for testing/demo27017❌ NoMongoDB intentionally private — only reachable from within the bridge network
Keeping the database port off the host follows standard security practice: the web and API layers are the public-facing entry points, and the database should never be directly reachable from outside the stack.
depends_on
yamldepends_on:
  - mongo
This tells Docker Compose to start mongo before app and worker. Without it, the Node.js app could attempt its MongoDB connection before the database is ready, causing a startup error. The db.js file also includes retry logic with a 5-second back-off as a belt-and-suspenders approach.

6. CloudLab Deployment
Prerequisites

A CloudLab account at cloudlab.us
This repository pushed to a public GitHub URL

Option A — Automated via CloudLab Profile (Recommended)

Log in to CloudLab and navigate to Experiments → Create Experiment.
Click Change Profile → Upload Profile and upload profile_docker.py.
Click Instantiate. The profile provisions a Ubuntu 22.04 XenVM, installs Docker, clones this repository, and runs docker compose up --build -d automatically.
Once the experiment status shows Ready, SSH into the node:

   ssh <your-cloudlab-username>@<node-hostname>

Verify the stack:

bash   docker compose ps
   docker compose logs -f

Open a browser and navigate to:

   http://<cloudlab-node-public-ip>:8080
Option B — Manual Setup

SSH into your CloudLab node.
Clone this repository:

bash   git clone https://github.com/AlexanderDimichele/csc466-docker-mongo
   cd csc466-docker-mongo

Run the bootstrap script:

bash   bash cloudlab/setup.sh

Log out and back in (required for the docker group to take effect), then deploy:

bash   bash scripts/deploy.sh
Verifying the Deployment
bash# All four containers should show as "Up"
docker compose ps

# Test the web app
curl -I http://localhost:8080

# Test the REST API
curl http://localhost:5000/api/games
curl http://localhost:5000/api/games/stats

# Watch worker logs polling the API
docker compose logs -f worker

# Run the full network test suite
bash scripts/network_test.sh

7. Automation Scripts
cloudlab/setup.sh
Bootstraps a fresh CloudLab Ubuntu 22.04 node with Docker Engine and the Compose plugin. Steps: update apt, install prerequisites, add Docker GPG key and apt repository, install Docker CE, add the current user to the docker group, enable and start the docker systemd service.
scripts/deploy.sh
Clones the repository if it is not already present, or pulls the latest changes if it is. Then tears down any running stack (docker compose down) and rebuilds and relaunches all services with docker compose up --build -d. Prints the public IP and direct URLs at the end.
scripts/network_test.sh
A seven-step connectivity verification script:

Lists running containers (docker compose ps)
Pings mongo from inside the app container (verifies DNS)
Checks TCP port 27017 is open inside the network
Verifies the web app responds on host port 8080
Verifies the API responds on host port 5000
Verifies the worker can reach the API over the internal network
Confirms MongoDB port 27017 is NOT reachable from the host

profile_docker.py
A GENI RSpec profile for CloudLab. Defines a single XenVM with Ubuntu 22.04, a routable control IP, and a sequence of rspec.Execute service calls that install Docker and deploy the full stack on experiment instantiation — no manual SSH required.

8. cgroups & Namespaces
Docker's isolation model is built on two Linux kernel features that are directly relevant to this class: namespaces and cgroups.
Namespaces create isolated views of system resources for each container. Each container in this stack gets its own network namespace (its own virtual network interface and routing table), PID namespace (processes inside cannot see processes in other containers), mount namespace (its own filesystem view), and UTS namespace (its own hostname). This is why the Node.js app container can resolve mongo as a hostname — Docker's DNS server lives in the network namespace and maps service names to container IPs.
cgroups (control groups) limit and account for resource usage. Docker uses cgroups to enforce CPU and memory limits per container, preventing one runaway service from starving the others. In this project, if the worker's polling loop were to spike CPU, cgroups would ensure it cannot consume resources allocated to the app or mongo containers.
Together, namespaces and cgroups are what make Docker containers lightweight yet isolated — they share the host kernel rather than running a full guest OS (unlike VMs), but still cannot interfere with each other.

9. Learning Outcomes
Multi-node deployment on CloudLab — Provisioned a Ubuntu 22.04 XenVM, installed Docker from scratch via apt, and deployed a four-container stack using a CloudLab RSpec profile. The automated profile_docker.py profile means the entire environment can be torn down and reprovisioned in minutes.
Automation scripts — Wrote setup.sh, deploy.sh, and network_test.sh in Bash with set -euo pipefail for safe error handling. Scripts handle idempotent behavior (clone only if not present, pull if already cloned) and print clear status output.
Infrastructure as code — The entire stack is defined declaratively in docker-compose.yml. Any developer can reproduce the exact environment with a single docker compose up command regardless of their local OS.
Networking between components — Gained hands-on experience with Docker bridge networks, automatic DNS resolution by service name, port publishing decisions (public vs. internal), and depends_on for startup ordering. The network_test.sh script verifies each connectivity assumption explicitly.
cgroups and namespaces — Applied course concepts by observing how Docker uses PID and network namespaces to isolate the four containers while running them on a shared Ubuntu 22.04 host kernel.
