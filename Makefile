up:
	docker compose up --build

down:
	docker compose -f docker-compose.yml down

clean:
	docker compose down -v --remove-orphans
	docker system prune -a --volumes
	docker compose build --no-cache
