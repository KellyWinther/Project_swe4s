#!/usr/bin/env bash
set -euo pipefail

test -e ssshtest || curl -s -o ssshtest 

source ssshtest

# run from root directory
# bash test/test_print_fires.sh

python="python3"
script="src/loading_utils.py"
data="test/test_data/subset_agrofood_co2_emission.csv"

run test_no_calculate $python $script \
    --country "Albania" \
    --country_column 0 \
    --fires_column 2 \
    --file_name $data 

    assert_in_stdout "Found 5 entries for 'Albania'"
    assert_in_stdout 5
    assert_in_stdout 5
    assert_in_stdout 5
    assert_in_stdout 5
    assert_in_stdout 5
    assert_exit_code 0