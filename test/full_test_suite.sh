#!/bin/bash

source test/test_suite_runner.sh test/test_suites/model_tests.txt
if [[ $? -ne 0 ]]; then
    return $?
fi

source test/test_suite_runner.sh test/test_suites/process_hierarchy_tests.txt
if [[ $? -ne 0 ]]; then
    return $?
fi

source test/test_suite_runner.sh test/test_suites/product_system_tests.txt
if [[ $? -ne 0 ]]; then
    return $?
fi

source test/test_suite_runner.sh test/test_suites/calculation_tests.txt
if [[ $? -ne 0 ]]; then
    return $?
fi
