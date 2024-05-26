build:
    docker-compose build

up:
    docker-compose up -d

down:
    docker-compose down

logs:
    docker-compose logs -f

scale-servers:
    docker-compose up -d --scale server=$(N) --no-recreate

.PHONY: build up down logs scale-servers