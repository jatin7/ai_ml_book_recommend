COMPOSE_BASE := docker compose
LOG_FILE := build.log

init-venv:
	python3 -m venv .venv

# pytest:
# 	pytest -v fastapi;

# RUN pip install --upgrade pip && \
#     pip install --no-cache-dir -r /app/requirements.txt

build-up:
	$(COMPOSE_BASE)	-f docker-compose.yaml up -d --build --remove-orphans;

up:	
	$(COMPOSE_BASE)	-f docker-compose.yaml up -d;

restart:	
	$(COMPOSE_BASE)	-f docker-compose.yaml restart;

down:
	$(COMPOSE_BASE)	-f docker-compose.yaml down;