.PHONY: build run clean test fmt lint install deps

# Build targets
build:
	cargo build --release

build-debug:
	cargo build

# Run targets
run:
	cargo run --release

run-debug:
	cargo run

# Development targets
clean:
	cargo clean

test:
	cargo test

test-show:
	cargo test -- --show-output

fmt:
	cargo fmt

lint:
	cargo clippy -- -D warnings

# Dependency targets
deps:
	cargo update

# Install (if needed)
install: build
	@echo "Binary available at: target/release/fractal-explorer"

# Help
help:
	@echo "Available targets:"
	@echo "  build        - Build release version"
	@echo "  build-debug  - Build debug version"
	@echo "  run          - Run release version"
	@echo "  run-debug    - Run debug version"
	@echo "  clean        - Clean build artifacts"
	@echo "  test         - Run tests"
	@echo "  test-show    - Run tests with output"
	@echo "  fmt          - Format code"
	@echo "  lint         - Run clippy lints"
	@echo "  deps         - Update dependencies"
	@echo "  install      - Build and show binary location"
	@echo "  help         - Show this help"
