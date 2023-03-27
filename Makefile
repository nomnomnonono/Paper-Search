.PHONY: build
build:
	docker-compose -f ./docker-compose.yml build paper_search

.PHONY: up
up:
	docker-compose -f ./docker-compose.yml up -d paper_search

.PHONY: exec
exec:
	docker exec -it paper_search bash

.PHONY: down
down:
	docker-compose -f ./docker-compose.yml down
