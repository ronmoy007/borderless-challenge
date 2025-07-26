# Run the orchestrator
run-producer:
	python producer/producers_orchestrator.py

# Run unit tests
test:
	python -m unittest discover -s producer -p "test_*.py"

compose:
	docker-compose up --build