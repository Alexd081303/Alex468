Base Images

Component	      Base Image	                        Reason
API Service	    python:3.11-slim	                  Lightweight, good for Flask
Worker	        node:alpine or python:3.11-slim	    Small footprint
OS	            Ubuntu 22.04 (CloudLab)	Matches     class environment

Technologies:

Containers using Docker

Network communication via REST

Automation via Bash + CloudLab profile

cgroups/namespaces concepts from class

Learning Goals:

Deploy multi-node application on CloudLab

Write automation scripts

Practice infrastructure as code

Understand networking between components
