#!/usr/bin/env bash

# set -xv

echo 'TEST: python unittests test script'

cd "$( dirname "${BASH_SOURCE[0]}" )" || exit 1
cd ../examples/cats || exit 1
./clean.sh

prepare_unittest_repos()
{
    # Clean and herd repo's to clean state
    ./init.sh
    clowder clean
    clowder herd
    # Remove jules repository
    rm -rf black-cats/jules
    # Make kishka repo dirty
    pushd black-cats/kishka &>/dev/null
    touch newfile
    git add .
    popd &>/dev/null
    # Set sasha repo to detached HEAD state
    pushd black-cats/sasha &>/dev/null
    git checkout '6ce5538d2c09fda2f56a9ca3859f5e8cfe706bf0'
    popd &>/dev/null
}

echo 'TEST: Prepare repos for unit tests'
prepare_unittest_repos
cd ../.. || exit 1
echo ''
echo '----------------------------------------------------------------------'
echo 'TEST: Run unittests'
echo ''
python3 -m unittest discover -v || exit 1

cd examples/cats || exit 1
./clean.sh
