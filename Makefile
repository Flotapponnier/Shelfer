# Makefile for AI SEO Analyzer

.PHONY: help backend-install backend-run frontend-install frontend-run all

help:
	@echo "Available commands:"
	@echo "  make backend-install   # Install backend Python dependencies using uv (not pip)"
	@echo "  make backend-run       # Run FastAPI backend server on port 8000 using uvicorn (dependencies managed by uv)"
	@echo "  make frontend-install  # Install frontend Node.js dependencies"
	@echo "  make frontend-run      # Run Next.js frontend development server on port 3000"
	@echo "  make all               # Install all dependencies (backend with uv & frontend)"

backend-install:
	cd backend && uv pip install -r requirements.txt

backend-run:
	cd backend && uvicorn main:app --reload --port 8000

frontend-install:
	cd frontend && npm install

frontend-run:
	cd frontend && npm run dev

all: backend-install frontend-install 