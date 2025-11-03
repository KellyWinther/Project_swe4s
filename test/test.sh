#!/usr/bin/env bash
set -euo pipefail

test -e ssshtest || curl -s -o ssshtest 

source ssshtest

# run from root directory
# bash test/test_print_fires.sh

python="python3"
script="src/loading_utils.py"
data="test/test_data/subset_agrofood_co2_emission.csv"

