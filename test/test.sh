test -e ssshtest || wget -q https://raw.githubusercontent.com/ryanlayer/ssshtest/master/ssshtest
. ssshtest

# Very basic valid call for testing purposes
run valid_call python src/example_call.py
assert_exit_code 0
assert_in_stdout "First ten rows of extracted data..."