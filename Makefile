# Run only orchestrator using Python Producer (redpanda and ClickHouse not running)
run-producer-python:	
	python producer/producers_orchestrator.py

# Run the orchestrator using Redpanda Connect (redpanda and ClickHouse not running)
run-producer-redpanda-connect:
	python producer/producers_orchestrator.py --redpanda-connect

# Run unit tests
unit-test:
	python -m unittest discover -s producer -p "test_*.py"

# Run all containers with python as producer
compose-producer-python:
	docker-compose -f docker-compose_producer_python.yaml up --build

# Run all containers with Redpanda Connect as producer
compose-producer-redpanda-connect:
	docker-compose -f docker-compose_producer_redpanda_connect.yaml up --build	

# Once all containers are running, its possible to query ClickHouse for the latest data
query:
	docker exec -it clickhouse_container clickhouse-client --query "SELECT * FROM kafka_physical ORDER BY trade_time DESC LIMIT 10;"
