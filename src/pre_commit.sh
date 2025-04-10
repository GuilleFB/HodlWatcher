#!/usr/bin/env bash

# run this script in src folder with ./scripts/pre_commit.sh

print_separator() {
    local title="$1"
    local width=60
    local padding=$(( (width - ${#title} - 2) / 2 ))
    local line=$(printf '%*s' "$width" | tr ' ' '═')

    echo ""
    echo "$line"
    printf "%*s %s %*s\n" $padding "" "$title" $padding ""
    echo "$line"
    echo ""
}

print_separator "ISORT: Organizing Imports"
isort .

print_separator "AUTOFLAKE: Deleting Unused Code"
autoflake -ri --remove-unused-variables --remove-all-unused-imports .

print_separator "BLACK: Formateando Código"
black .

print_separator "BANDIT: Security Analysis"
bandit -r . -ll

print_separator "SAFETY: Checking Dependencies"
safety scan

print_separator "PYTEST and COVERAGE: Checking Tests and Coverage"
coverage run -m pytest .
coverage report

print_separator "PRE-COMMIT COMPLETADO"
echo "All analyses and formatting have been executed correctly."
echo ""
echo "Please verify the changes before committing."
echo ""
