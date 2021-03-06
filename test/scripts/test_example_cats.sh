#!/usr/bin/env bash

# set -xv

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" || exit 1

. test_utilities.sh

print_double_separator
echo 'TEST: cats example test script'
print_double_separator

test_clowder_version
test_command

"$TEST_SCRIPT_DIR/cats/init.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/branch.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/status.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/clean.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/herd.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/herd_branch.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/herd_tag.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/forall.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/save.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/stash.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/link.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/yaml_validation.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/start.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/prune.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/repo.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/reset.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/yaml.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/import.sh" || exit 1
"$TEST_SCRIPT_DIR/cats/help.sh" || exit 1
