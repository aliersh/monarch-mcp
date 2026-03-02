#!/usr/bin/env bash
# Local CI check — same steps as .github/workflows/ci.yml
# Run with: ./scripts/ci.sh  or  bash scripts/ci.sh
set -euo pipefail

red='\033[0;31m'
green='\033[0;32m'
bold='\033[1m'
reset='\033[0m'

pass() { echo -e "${green}✓${reset} $1"; }
fail() { echo -e "${red}✗${reset} $1"; exit 1; }

echo -e "${bold}Running CI checks...${reset}"
echo

uv run ruff check . && pass "ruff check" || fail "ruff check"
uv run ruff format --check . && pass "ruff format" || fail "ruff format"
uv run mypy server.py && pass "mypy" || fail "mypy"
uv run pytest tests/ --tb=short -q && pass "tests" || fail "tests"

echo
echo -e "${green}${bold}All checks passed.${reset}"
