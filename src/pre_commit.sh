#!/usr/bin/env bash

# run this script in src folder with ./scripts/pre_commit.sh

echo ..isort
isort .
echo ..autoflake
autoflake -ri --remove-unused-variables --remove-all-unused-imports .
echo ..black
black .
