## Installation

Copy `.env.example` to `.env` and make necessary modifications.
* WEB_PORT -- port of the web server (only required on server)
* REDIS_HOST -- hostname of the redis broker (only required on worker)
* REDIS_PASSWORD -- password for the redis broker
* DRY_RUN -- if set to `True`, worker will log printing commands instead of actually running them

### Server
Run `docker-compose up -d`.
Dependencies:
* docker
* docker-compose 3.9

### Worker
Run `./install_worker.sh`, then `./run_worker.sh`.
Dependencies:
* python3-venv
* a2ps
* lp

