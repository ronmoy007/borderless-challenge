# Run the orchestrator
run:
	python producer/producers_orchestrator.py

# Run unit tests
test:
	python -m unittest discover -s producer -p "test_*.py"
