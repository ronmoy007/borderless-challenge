# Run the orchestrator
run-producer:
	python producer/producers_orchestrator.py

# Run unit tests
test:
	python -m unittest discover -s producer -p "test_*.py"

compose:
	docker-compose up --build

query:
	docker exec -it clickhouse_service clickhouse-client --query "SELECT * FROM kafka_physical ORDER BY trade_time DESC LIMIT 10;"
