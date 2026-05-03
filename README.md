Alex468





<img width="900" height="400" alt="project_vision_diagram" src="https://github.com/user-attachments/assets/911df427-5ee2-4938-9e48-87ead86019cb" />

# CSC 466 — Docker + MongoDB Video Game App

A fully containerized, multi-service web application where users can submit their favorite video games and genres. Data is stored in MongoDB and displayed back in the browser. A Python Flask REST API and a background worker service round out a three-tier architecture deployed on CloudLab.

**Developed by Alexander Dimichele**

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Folder Structure](#2-folder-structure)
3. [Container Design & Base Images](#3-container-design--base-images)
4. [Dockerfile Walkthrough](#4-dockerfile-walkthrough)
5. [Networking](#5-networking)
6. [CloudLab Deployment](#6-cloudlab-deployment)
7. [Automation Scripts](#7-automation-scripts)
8. [cgroups & Namespaces](#8-cgroups--namespaces)
9. [Learning Outcomes](#9-learning-outcomes)

---

## 1. System Architecture
```
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
```

The system consists of four services:

**app** — A Node.js/Express web server that renders HTML views using EJS. It accepts game submissions from the browser, writes them to MongoDB, and displays the full game list. Exposed on port 8080.

**api** — A Python Flask REST API that reads game data from MongoDB and exposes it as JSON. It provides a `/api/games` endpoint for the full game list and `/api/games/stats` for genre breakdowns. Exposed on port 5000.

**worker** — A Python background service that polls the API every 30 seconds and logs game statistics to stdout. It demonstrates persistent inter-service communication over the internal network without any exposed ports.

**mongo** — The official MongoDB 6 image used as a shared data store. Its data is persisted to a named Docker volume so game entries survive container restarts. Its port is intentionally not published to the host.

---

## 2. Folder Structure
```
csc466-docker-mongo/
├── docker-compose.yml
├── profile_docker.py
├── cloudlab/
│   └── setup.sh
├── scripts/
│   ├── deploy.sh
│   └── network_test.sh
├── docker/
│   ├── Dockerfile
│   ├── package.json
│   ├── app.js
│   ├── db.js
│   ├── controllers/
│   │   └── games.js
│   ├── models/
│   │   └── games.js
│   ├── routes/
│   │   └── games.js
│   └── views/
│       ├── index.html
│       ├── games.html
│       ├── getgame.html
│       └── css/
│           └── styles.css
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
└── worker/
    ├── Dockerfile
    ├── requirements.txt
    └── worker.py
```

---

## 3. Container Design & Base Images

| Service | Base Image | Reason |
|---------|------------|--------|
| app | `node:alpine` | Minimal Node.js image (~50 MB vs 350 MB+). No system-level dependencies needed. |
| api | `python:3.11-slim` | Slim Debian variant, lightweight and compatible with pip packages. |
| worker | `python:3.11-slim` | Same reasoning as the API. |
| mongo | `mongo:6` | Official image, stable long-term release with strong Mongoose compatibility. |

Alpine Linux is chosen for the Node.js service because it produces significantly smaller images. Smaller images pull faster on CloudLab, use less disk, and have a smaller attack surface. The Python services use `python:3.11-slim` rather than Alpine because some pip packages require C build tooling that is awkward to install on Alpine.

---

## 4. Dockerfile Walkthrough

### Node.js App

```dockerfile
FROM node:alpine
```
Pulls the official Node.js image on Alpine Linux — minimal footprint, fast build.

```dockerfile
RUN mkdir -p /home/node/app/node_modules && chown -R node:node /home/node/app
```
Creates the app directory and hands ownership to the built-in node user. Running as non-root is a security best practice.

```dockerfile
COPY package*.json ./
RUN npm install
```
Copies only the package files before the source code. This exploits Docker layer caching — as long as package.json has not changed, the npm install layer is reused on every rebuild.

```dockerfile
COPY --chown=node:node . .
USER node
EXPOSE 8080
CMD ["node", "app.js"]
```
Copies source code, switches to unprivileged user, documents the port, and starts the app as PID 1 for proper signal handling.

### Python API and Worker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```
Same layer-caching strategy — requirements are only reinstalled when that file changes. `--no-cache-dir` keeps the image size down.

---

## 5. Networking

### Bridge Network

Docker Compose automatically creates a named bridge network called `app-network` for all services. A bridge network is a private internal network on the host — containers on it can reach each other directly using service names as hostnames, while remaining isolated from the public internet unless ports are explicitly published.

### DNS Resolution

Docker provides automatic DNS resolution within the bridge network. Each service name becomes a resolvable hostname. This is why the MongoDB connection uses `mongo` as the hostname rather than an IP address:

```javascript
const url = `mongodb://${MONGO_HOSTNAME}:${MONGO_PORT}/${MONGO_DB}`;
// MONGO_HOSTNAME defaults to 'mongo' — resolved by Docker's internal DNS
```

The worker calls `http://api:5000/health` to reach the Flask service — Docker DNS resolves `api` automatically.

### Port Publishing

| Port | Published to Host | Purpose |
|------|-------------------|---------|
| 8080 | Yes | Web app accessible from browser |
| 5000 | Yes | API accessible for testing |
| 27017 | No | MongoDB intentionally private |

### depends_on

```yaml
depends_on:
  - mongo
```

Tells Docker Compose to start mongo before app and worker. The db.js file also includes retry logic with a 5-second back-off as an additional safeguard.

---

## 6. CloudLab Deployment

### Prerequisites
- A CloudLab account at cloudlab.us
- This repository pushed to a public GitHub URL

### Steps

1. Log in to CloudLab and navigate to Experiments → Create Experiment
2. Click Change Profile → Upload Profile and upload `profile_docker.py`
3. Click Instantiate and wait for status to show Ready
4. SSH into the node and run:

```bash
git clone -b Docker https://github.com/Alexd081303/Alex468.git
cd Alex468
docker compose up --build -d
```

5. Get your public IP and open the app:

```bash
curl ifconfig.me
# then open http://<ip>:8080 in browser
```

### Verifying

```bash
docker compose ps
curl http://localhost:5000/api/games
bash scripts/network_test.sh
```

---

## 7. Automation Scripts

**cloudlab/setup.sh** — Bootstraps a fresh CloudLab Ubuntu 22.04 node with Docker Engine and the Compose plugin.

**scripts/deploy.sh** — Clones the repository if not already present, or pulls latest changes. Then tears down any running stack and rebuilds all services with `docker compose up --build -d`.

**scripts/network_test.sh** — A seven-step connectivity verification script that checks DNS resolution, TCP connectivity, HTTP responses on ports 8080 and 5000, worker-to-API communication, and confirms MongoDB is not exposed to the host.

**profile_docker.py** — A GENI RSpec profile for CloudLab. Defines a single XenVM with Ubuntu 22.04 and a sequence of Execute service calls that install Docker and deploy the full stack automatically on experiment instantiation.

---

## 8. cgroups & Namespaces

Docker's isolation model is built on two Linux kernel features covered in class: namespaces and cgroups.

**Namespaces** create isolated views of system resources for each container. Each container gets its own network namespace (its own virtual network interface), PID namespace (processes cannot see other containers), mount namespace (its own filesystem view), and UTS namespace (its own hostname). This is why the Node.js app container can resolve `mongo` as a hostname — Docker's DNS server lives in the network namespace and maps service names to container IPs.

**cgroups** limit and account for resource usage per container. Docker uses cgroups to enforce CPU and memory limits, preventing one runaway service from starving the others. If the worker's polling loop were to spike CPU, cgroups ensure it cannot consume resources allocated to the app or mongo containers.

Together, namespaces and cgroups make Docker containers lightweight yet isolated — they share the host kernel rather than running a full guest OS like a VM, but still cannot interfere with each other.

---

## 9. Learning Outcomes

**Multi-node deployment on CloudLab** — Provisioned a Ubuntu 22.04 XenVM, installed Docker from scratch via apt, and deployed a four-container stack using a CloudLab RSpec profile.

**Automation scripts** — Wrote setup.sh, deploy.sh, and network_test.sh in Bash with `set -euo pipefail` for safe error handling. Scripts handle idempotent behavior and print clear status output.

**Infrastructure as code** — The entire stack is defined declaratively in docker-compose.yml. Any developer can reproduce the exact environment with a single `docker compose up` command.

**Networking between components** — Gained hands-on experience with Docker bridge networks, automatic DNS resolution by service name, port publishing decisions, and depends_on for startup ordering.

**cgroups and namespaces** — Applied course concepts by observing how Docker uses PID and network namespaces to isolate the four containers while running them on a shared Ubuntu 22.04 host kernel.
