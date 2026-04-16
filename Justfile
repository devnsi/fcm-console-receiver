#!/usr/bin/env just --justfile

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
set windows-shell := ["sh.exe", "-eu", "-o", "pipefail", "-c"]
set quiet := true

version := `yq '.project.version' pyproject.toml`
bin := "fcm-console-receiver"

# Explain how to use the recipes.
[default]
[private]
default:
    just --list

# Set up the development environment.
setup:
    uv sync --all-groups

# Run the application.
[group("execute")]
run *flags:
    -uv run -m fcm_console_receiver ""{{ flags }}

# Run the application (reloading on file changes).
[group("execute")]
watch *flags:
    -watchexec -r -e py -- uv run -m fcm_console_receiver ""{{ flags }}

# Run the tests.
[group("execute")]
test *flags:
    uv run ruff check .
    uv run pytest ""{{ flags }}

# Build the wheel.
[group("package")]
build:
    mkdir -p build
    uv build
    unzip -l dist/*.whl > build/content.txt

# Install as (uv-wrapped) executable tool.
[group("package")]
[script]
install: build
    latest=$(ls -t dist | grep .whl | head -n 1)
    uv tool install "dist/$latest" --force
    ~/.local/bin/fcm-console-receiver.exe --help

# Bundle to (standalone) executable.
[group("package")]
bundle:
    uv run pyinstaller --onefile \
      --name "fcm-console-receiver.exe" \
      --noconfirm \
      --specpath ./build \
      src/fcm_console_receiver/show_notifications.py
    ./dist/fcm-console-receiver.exe --help

# Containerize for linux.
[group("package")]
container:
    docker build -t "{{ bin }}:latest" .
    docker tag "{{ bin }}:latest" "{{ bin }}:{{ version }}"
    docker run -t --rm "{{ bin }}:latest" fcm-console-receiver --help
