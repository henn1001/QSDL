#!/bin/bash

init() {
  uv sync --all-extras

  # init vscode
  for file in launch.json settings.json; do
    if [ ! -f ".vscode/$file" ] && [ -f ".vscode/${file}.template" ]; then
      cp ".vscode/${file}.template" ".vscode/$file"
    fi
  done
}

lint() {
  ruff format
  ruff check "$@"
}

tests() {
  uv run pytest
}

build() {
  uv build
}

build-docker() {
  docker build -t qsdl .
}

release (){
  npx standard-version
}

clean() {
  echo "cleaning..."
  rm -rf .pytest_cache/ .ruff_cache/ dist/ .coverage srcgen/
  find src tests -type d \
    \( -name "*.egg-info" -o -name "__pycache__" \) \
    -exec rm -rf {} +
}

# Dynamically dispatch to functions
if false; then
  echo
elif declare -F "$1" >/dev/null && [[ "$1" != _* ]]; then
  "$@"
else
  echo "Usage: $(basename "$0") [OPTIONS]"
  echo
  echo -e "\033[1;4;32m""Options:""\033[0;34m"
  compgen -A function | grep -v '^_'
  echo -e "\033[0m"
fi