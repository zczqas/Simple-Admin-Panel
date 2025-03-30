dev:
	@docker-compose --env-file .env up --build -d
dev-down:
	@docker-compose down
dev-logs:
	@docker-compose logs -f
test:
	@docker-compose exec api pytest -xvs app/tests/$(test).py