.PHONY: help install temporal-start temporal-stop worker client run clean

# Default target
help:
	@echo "Available targets:"
	@echo "  make install        - Install project dependencies using uv"
	@echo "  make temporal-start - Start Temporal development server"
	@echo "  make temporal-stop  - Stop Temporal development server"
	@echo "  make worker         - Run the Temporal worker"
	@echo "  make client         - Run the client to start a workflow"
	@echo "  make run            - Start Temporal server, worker, and client (all-in-one)"
	@echo "  make clean          - Clean up generated files"

# Install dependencies
install:
	@echo "Installing dependencies with uv..."
	uv sync

# Start Temporal development server
temporal-start:
	@echo "Starting Temporal development server..."
	@echo "Note: This will run in the foreground. Press Ctrl+C to stop."
	temporal server start-dev

# Stop Temporal development server (if running in background)
temporal-stop:
	@echo "Stopping Temporal development server..."
	@pkill -f "temporal server start-dev" || true

# Run the worker
worker:
	@echo "Starting Temporal worker..."
	python worker.py

# Run the client
client:
	@echo "Starting client..."
	python client.py

# Run everything: temporal server, worker, and client
run:
	@echo "Starting Temporal development server in background..."
	@temporal server start-dev > /dev/null 2>&1 & \
	TEMPORAL_PID=$$!; \
	echo "Temporal server started (PID: $$TEMPORAL_PID)"; \
	echo "Waiting for Temporal server to be ready..."; \
	sleep 5; \
	echo "Starting worker in background..."; \
	python worker.py > worker.log 2>&1 & \
	WORKER_PID=$$!; \
	echo "Worker started (PID: $$WORKER_PID)"; \
	echo "Waiting for worker to initialize..."; \
	sleep 3; \
	echo "Starting client..."; \
	python client.py; \
	echo ""; \
	echo "Cleaning up background processes..."; \
	kill $$WORKER_PID 2>/dev/null || true; \
	kill $$TEMPORAL_PID 2>/dev/null || true; \
	echo "Done. Check worker.log for worker output."

# Clean up generated files
clean:
	@echo "Cleaning up..."
	@rm -f *.pdf
	@rm -f worker.log
	@rm -rf __pycache__
	@rm -rf .ruff_cache
	@echo "Clean complete."
