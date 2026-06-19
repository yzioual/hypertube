all: build run

run:
	docker compose up -d

run build :
	docker compose up --build

stop:
	docker compose stop

clean:
	docker compose down -v

fclean: clean
	docker system prune -af

db:
	docker compose exec db psql -U hypertube -d hypertube

re: stop run
