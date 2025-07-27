# First 2 options are only fur development purposes, they run the orchestrator without Redpanda and ClickHouse.
# Run only orchestrator using Python Producer (redpanda and ClickHouse not running)
# run-producer-python:	
# 	python producers/producers_orchestrator.py

# Run the orchestrator using Redpanda Connect (redpanda and ClickHouse not running)
# run-producer-redpanda-connect:
# 	python producers/producers_orchestrator.py --redpanda-connect

# Run unit tests
unit-test:
	python -m unittest discover -s producers -p "test_*.py"

# Run all containers with python as producer
compose-producer-python:
	docker-compose -f docker-compose_producer_python.yaml up --build

# Run all containers with Redpanda Connect as producer
compose-producer-redpanda-connect:
	docker-compose -f docker-compose_producer_redpanda_connect.yaml up --build	

# Once all containers are running, its possible to query ClickHouse for the latest data
query-verify-data-exists:
	docker exec -it clickhouse_container clickhouse-client --query " \
		SELECT * \
		FROM kafka_physical \
		ORDER BY trade_time DESC LIMIT 10 \
		;"

query-verify-materialized-view:
	docker exec -it clickhouse_container clickhouse-client --query " \
		SELECT * \
		FROM kafka_materialized_view \
		ORDER BY trade_time DESC LIMIT 10 \
		;"

query-count-trades_by-symbol:
	docker exec -it clickhouse_container clickhouse-client --query " \
		SELECT symbol, COUNT(*) as trade_count \
		FROM kafka_physical \
		GROUP BY symbol \
		ORDER BY trade_count \
		DESC LIMIT 10 \
		;"

query-no-empty-fields: # This query always should return 0, due to the fact that the producer is designed to not send empty fields.
	docker exec -it clickhouse_container clickhouse-client --query " \
		SELECT COUNT(*) \
		FROM kafka_physical \
		WHERE event_type IS NULL \
		OR event_time IS NULL \
		OR symbol IS NULL \
		OR trade_id IS NULL \
		OR price IS NULL \
		OR quantity IS NULL \
		OR trade_time IS NULL \
		OR is_market_maker IS NULL \
		OR ignore IS NULL \
		;"

query-for-duplicates:  # This query should return 0, because the producer is designed to not send duplicate trades by symbol.
	docker exec -it clickhouse_container clickhouse-client --query " \
		SELECT symbol, trade_id, COUNT(*) as count \
		FROM kafka_physical \
		GROUP BY symbol, trade_id \
		HAVING count > 1 \
		;"

enter-clickhouse-container-for-querying:
	docker exec -it clickhouse_container clickhouse-client
