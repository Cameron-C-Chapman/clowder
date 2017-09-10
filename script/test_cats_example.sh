#!/usr/bin/env bash

# set -xv

echo 'TEST: cats example test script'

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" || exit 1

if [ -n "$TRAVIS_OS_NAME" ]; then
    if [ "$TRAVIS_OS_NAME" = "osx" ]; then
        ./unittests.sh || exit 1
    fi
fi

source test_utilities.sh
cd ../examples/cats || exit 1
./clean.sh

export projects=( 'black-cats/kit' \
                  'black-cats/kishka' \
                  'black-cats/sasha' \
                  'black-cats/jules' )

test_init_branch()
{
    print_separator
    echo "TEST: Test clowder init branch"

    clowder init https://github.com/jrgoodle/cats.git -b tags

    pushd .clowder &>/dev/null
    test_branch tags
    popd &>/dev/null

    rm -rf .clowder clowder.yaml
}
test_init_branch

test_command
test_clowder_version
test_init_herd_version
test_branch_version "${projects[@]}"
test_init_herd

test_branches()
{
    test_branch_master "${projects[@]}"
    pushd mu &>/dev/null
    test_branch knead
    popd &>/dev/null
    pushd duke &>/dev/null
    test_branch purr
    popd &>/dev/null
}
test_branches

test_status_groups 'black-cats'
test_status_projects 'jrgoodle/mu' 'jrgoodle/duke'

test_clean()
{
    print_separator
    make_dirty_repos "${projects[@]}"
    echo "TEST: Clean specific group when dirty"
    clowder clean -g "$@" || exit 1
    clowder status || exit 1
    echo "TEST: Clean all when dirty"
    clowder clean || exit 1
    clowder status || exit 1
    echo "TEST: Clean when clean"
    clowder clean || exit 1
}
test_clean 'black-cats'

test_clean_projects()
{
    print_separator
    make_dirty_repos "${projects[@]}"
    echo "TEST: Clean specific project when dirty"
    clowder clean -p "$@" || exit 1
    clowder status || exit 1
    echo "TEST: Clean all when dirty"
    clowder clean || exit 1
    clowder status || exit 1
}
test_clean_projects 'jrgoodle/kit'

test_clean_missing_directories 'mu' 'duke'
test_herd_dirty_repos "${projects[@]}"
test_herd_detached_heads "${projects[@]}"
test_herd 'duke' 'mu'
test_forall 'cats'
test_forall_projects 'jrgoodle/kit' 'jrgoodle/kishka'
test_save

test_stash()
{
    make_dirty_repos "${projects[@]}"
    echo "TEST: Fail herd with dirty repos"
    clowder herd && exit 1
    echo "TEST: Stash specific groups when dirty"
    clowder stash -g "$@" || exit 1
    clowder status || exit 1
    echo "TEST: Stash all changes when dirty"
    clowder stash || exit 1
    clowder status || exit 1
    echo "TEST: Stash changes when clean"
    clowder stash || exit 1
}
test_stash 'black-cats'

test_stash_projects()
{
    make_dirty_repos "${projects[@]}"
    echo "TEST: Stash specific projects when dirty"
    clowder stash -p "$@" || exit 1
    clowder status || exit 1
    echo "TEST: Stash all changes when dirty"
    clowder stash || exit 1
    clowder status || exit 1
}
test_stash_projects 'jrgoodle/kit'

test_stash_missing_directories 'mu' 'duke'
test_herd_groups 'cats'

test_herd_missing_branches()
{
    print_separator
    echo "TEST: Herd v0.1 to test missing default branches"
    clowder link -v v0.1 || exit 1
    clowder herd || exit 1
    echo "TEST: Delete default branches locally"
    pushd mu &>/dev/null
    git branch -D knead
    popd &>/dev/null
    pushd duke &>/dev/null
    git branch -D purr
    popd &>/dev/null
    echo "TEST: Herd existing repo's with no default branch locally"
    clowder link || exit 1
    clowder herd || exit 1
    clowder status || exit 1
}
test_herd_missing_branches

test_save_missing_directories 'duke' 'mu'

test_no_versions()
{
    print_separator
    echo "TEST: Test clowder repo with no versions saved"
    clowder repo checkout no-versions || exit 1
    clowder link -v saved-version && exit 1
    clowder herd || exit 1
    clowder status || exit 1
    clowder repo checkout master || exit 1
}
test_no_versions

test_herd_projects 'jrgoodle/kit' 'jrgoodle/kishka'

test_invalid_yaml()
{
    print_separator
    echo "TEST: Fail herd with invalid yaml"

    clowder repo checkout invalid-yaml || exit 1

    test_cases=( 'missing-defaults' \
                 'missing-sources' \
                 'missing-groups' \
                 'missing-default-arg' \
                 'missing-source-arg' \
                 'missing-group-arg' \
                 'missing-project-arg' \
                 'missing-fork-arg' \
                 'unknown-defaults-arg' \
                 'unknown-source-arg' \
                 'unknown-project-arg' \
                 'unknown-fork-arg' )

    for test in "${test_cases[@]}"
    do
        clowder link -v $test || exit 1
        clowder herd && exit 1
        rm clowder.yaml
    done

    pushd .clowder &>/dev/null
    git checkout master
    popd &>/dev/null
}
test_invalid_yaml

test_herd_sha()
{
    print_separator
    echo "TEST: Test herd of static commit hash refs"
    clowder repo checkout static-refs || exit 1
    clowder herd || exit 1
    clowder status || exit 1
    clowder repo checkout master || exit 1
}
test_herd_sha

test_herd_tag()
{
    print_separator
    echo "TEST: Test herd of tag refs"
    clowder repo checkout tags || exit 1
    clowder herd || exit 1
    clowder status || exit 1
    clowder repo checkout master || exit 1
}
test_herd_tag

test_start()
{
    clowder herd
    print_separator
    echo "TEST: Start new feature branch"

    clowder start start_branch
    # TODO: clowder herd -b
    # clowder herd -b master -g black-cats
    clowder forall -g black-cats -c 'git fetch origin master'
    clowder forall -g black-cats -c 'git checkout master'

    pushd mu &>/dev/null
    test_branch start_branch
    popd &>/dev/null
    pushd duke &>/dev/null
    test_branch start_branch
    popd &>/dev/null
    pushd black-cats/jules &>/dev/null
    test_branch master
    popd &>/dev/null
    pushd black-cats/kishka &>/dev/null
    test_branch master
    popd &>/dev/null

    clowder start start_branch

    pushd black-cats/jules &>/dev/null
    test_branch start_branch
    popd &>/dev/null
    pushd black-cats/kishka &>/dev/null
    test_branch start_branch
    popd &>/dev/null
}
test_start

test_prune()
{
    clowder herd
    print_separator
    echo "TEST: Test clowder prune branch"

    clowder start prune_branch
    clowder prune prune_branch

    pushd black-cats/jules &>/dev/null
    test_branch master
    popd &>/dev/null
    pushd black-cats/kishka &>/dev/null
    test_branch master
    popd &>/dev/null

    clowder start prune_branch
    clowder prune prune_branch -g black-cats

    pushd duke &>/dev/null
    test_branch prune_branch
    popd &>/dev/null
    pushd mu &>/dev/null
    test_branch prune_branch
    popd &>/dev/null
    pushd black-cats/jules &>/dev/null
    test_branch master
    popd &>/dev/null
    pushd black-cats/kishka &>/dev/null
    test_branch master
    popd &>/dev/null

    echo "TEST: Test clowder force prune branch"

    clowder start prune_branch
    pushd duke &>/dev/null
    touch something
    git add something
    git commit -m 'something'
    popd &>/dev/null
    pushd mu &>/dev/null
    touch something
    git add something
    git commit -m 'something'
    popd &>/dev/null

    clowder prune prune_branch && exit 1
    clowder prune -f prune_branch || exit 1

    pushd duke &>/dev/null
    test_branch purr
    popd &>/dev/null
    pushd mu &>/dev/null
    test_branch knead
    popd &>/dev/null

    if [ -z "$TRAVIS_OS_NAME" ]; then
        echo "TEST: Test clowder prune remote branch"

        pushd duke &>/dev/null
        git checkout -b remote_branch
        git push -u origin remote_branch
        popd &>/dev/null

        clowder prune remote_branch

        pushd duke &>/dev/null
        OUT_1="$(git ls-remote --heads origin remote_branch | wc -l | tr -d '[:space:]')"
        if [ "$OUT_1" -eq "0" ]; then
            exit 1
        fi
        popd

        clowder prune -r remote_branch

        pushd duke &>/dev/null
        OUT_2="$(git ls-remote --heads origin remote_branch | wc -l | tr -d '[:space:]')"
        if [ "$OUT_2" -eq "1" ]; then
            exit 1
        fi
        popd
    fi
}
test_prune

test_clowder_repo()
{
    print_separator
    echo "TEST: Test clowder repo command"
    clowder repo checkout ref_that_doesnt_exist && exit 1
    clowder repo add file_that_doesnt_exist && exit 1
}
test_clowder_repo

test_clowder_import()
{
    print_separator

    echo "TEST: Test clowder file with default import"
    clowder link
    clowder herd
    clowder link -v import-default
    clowder herd
    pushd black-cats/jules &>/dev/null
    test_branch import-default
    popd &>/dev/null
    pushd black-cats/kishka &>/dev/null
    test_branch import-default
    popd &>/dev/null
    pushd black-cats/kit &>/dev/null
    test_branch import-default
    popd &>/dev/null
    pushd black-cats/sasha &>/dev/null
    test_branch import-default
    popd &>/dev/null

    echo "TEST: Test clowder file with version import"
    clowder link
    clowder herd
    clowder link -v import-version
    clowder herd
    pushd black-cats/jules &>/dev/null
    test_branch import-version
    popd &>/dev/null
    pushd black-cats/kishka &>/dev/null
    test_branch import-version
    popd &>/dev/null
    pushd black-cats/kit &>/dev/null
    test_branch import-version
    popd &>/dev/null
    pushd black-cats/sasha &>/dev/null
    test_branch import-version
    popd &>/dev/null

    echo "TEST: Test clowder file with infinite import loop"
    clowder link
    clowder herd
    clowder link -v import-loop-1
    clowder herd && exit 1
}
test_clowder_import

print_help
