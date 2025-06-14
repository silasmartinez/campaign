# Campaign Assistant - Development Makefile

.PHONY: check-system install dev-install test clean format lint run-test start help doctor

# Default target
help:
	@echo "Campaign Assistant - Available Commands:"
	@echo "========================================"
	@echo "check-system - Check system requirements and dependencies"
	@echo "doctor       - Diagnose issues and suggest fixes"
	@echo "install      - Install production dependencies"
	@echo "dev-install  - Install development dependencies"
	@echo "test         - Run the test suite"
	@echo "format       - Format code with black and isort"
	@echo "lint         - Run linting checks"
	@echo "run-test     - Run the campaign test script"
	@echo "start        - Start the Campaign Assistant"
	@echo "clean        - Clean up generated files"
	@echo "help         - Show this help message"

# Check system requirements
check-system:
	@echo "🔍 Checking system requirements..."
	@./scripts/check_system.sh

# Doctor - diagnose and suggest fixes
doctor:
	@echo "🩺 Running system diagnostics..."
	@./scripts/doctor.sh

# Install production dependencies
install: check-system
	@echo "🎲 Installing Campaign Assistant..."
	@./install.sh

# Install development dependencies
dev-install: install
	@echo "🔧 Installing development dependencies..."
	@source venv/bin/activate && pip install -e ".[dev]"

# Run tests
test:
	@echo "🧪 Running tests..."
	@source venv/bin/activate && python -m pytest tests/ -v

# Format code
format:
	@echo "✨ Formatting code..."
	@source venv/bin/activate && black src/ main.py test_campaign.py
	@source venv/bin/activate && isort src/ main.py test_campaign.py

# Lint code
lint:
	@echo "🔍 Linting code..."
	@source venv/bin/activate && black --check src/ main.py test_campaign.py
	@source venv/bin/activate && isort --check-only src/ main.py test_campaign.py

# Run the campaign test script
run-test:
	@echo "🎯 Running campaign test..."
	@source venv/bin/activate && python test_campaign.py

# Start the Campaign Assistant
start:
	@echo "🚀 Starting Campaign Assistant..."
	@source venv/bin/activate && python main.py

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf venv/
	@rm -rf data/
	@rm -rf __pycache__/
	@rm -rf src/__pycache__/
	@rm -rf src/*/__pycache__/
	@rm -rf .pytest_cache/
	@rm -rf *.egg-info/
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete

# Quick start - install and test
quickstart: check-system install run-test
	@echo "🎉 Quick start complete!"

# Auto-fix common issues (macOS specific)
fix-macos:
	@echo "🔧 Attempting to fix common macOS issues..."
	@./scripts/fix_macos.sh