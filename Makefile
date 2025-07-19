# Makefile for AI SEO Analyzer
#
# Usage:
#   make help         # Show all available commands and what they do
#   make backend-install  # Install backend Python dependencies using uv
#   make backend-run      # Kill process on port 8000 if needed, then run FastAPI backend
#   make frontend-install # Install frontend Node.js dependencies
#   make frontend-run     # Run Next.js frontend development server
#   make kill-backend-port # Kill any process running on backend port (default: 8000)
#   make init             # Install all dependencies (backend & frontend)
#   make test-html-extractor        # Run HTML extractor service test (22 properties)
#   make test-image-extractor       # Run image extractor service test (10 properties)
#   make test-all         # Run all extractor service tests
#
# For more details, run: make help

.PHONY: help backend-install backend-run frontend-install frontend-run kill-backend-port init test-html test-image test-all

# Default backend port (change if needed)
BACKEND_PORT ?= 8000

# Show all available commands and what they do
help:
	@echo "Available commands:"
	@echo "  make backend-install    			# Install backend Python dependencies using uv (not pip)"
	@echo "  make backend-run        			# Kill process on port $(BACKEND_PORT) if needed, then run FastAPI backend server on port $(PORT) using uvicorn (dependencies managed by uv)"
	@echo "  make frontend-install   			# Install frontend Node.js dependencies"
	@echo "  make frontend-run       			# Run Next.js frontend development server on port 3000"
	@echo "  make kill-backend-port  			# Kill process running on port $(BACKEND_PORT) (macOS only)"
	@echo "  make init               			# Install all dependencies (backend with uv & frontend)"
	@echo "  make test-html-extractor     # Run HTML extractor service test (22 properties)"
	@echo "  make test-image-extractor    # Run image extractor service test (10 properties)"
	@echo "  make test-all           			# Run all extractor service tests"

# Install backend Python dependencies using uv
backend-install:
	cd backend && uv sync

# Kill any process running on the backend port (default: $(PORT))
kill-backend-port:
	@PID=$$(lsof -ti tcp:$(BACKEND_PORT)); \
	if [ -n "$$PID" ]; then \
		echo "Killing process on port $(BACKEND_PORT) (PID: $$PID)"; \
		kill -9 $$PID; \
	else \
		echo "No process running on port $(BACKEND_PORT)"; \
	fi

# Run FastAPI backend server, killing any process on the port first
backend-run: kill-backend-port
	cd backend && uvicorn app:app --reload --port $(BACKEND_PORT)

# Install frontend Node.js dependencies
frontend-install:
	cd frontend && npm install

# Run Next.js frontend development server
frontend-run:
	cd frontend && npm run dev

# Install all dependencies (backend & frontend)
init: backend-install frontend-install 

fetch_schema:
	cd backend && python scripts/fetch_product_schema.py

# Run HTML extractor service test
test-html-extractor:
	cd backend && uv run python tests/test_html_extractor.py

# Run image extractor service test  
test-image-extractor:
	cd backend && uv run python tests/test_image_extractor.py

# Run all extractor service tests
test-all: test-html-extractor test-image-extractor