#!/usr/bin/env bash

TEST_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

make_dirty_clowder_repo()
{
    echo "TEST: Make dirty clowder repo"
    clowder repo run 'touch newfile' || exit 1
    clowder repo add newfile || exit 1
    clowder status -f || exit 1
}

make_dirty_repos()
{
    echo "TEST: Make dirty repos"
    for project in "$@"
    do
    	pushd $project
        touch newfile
        git add newfile
        popd
    done
    clowder status -v || exit 1
}

test_branch()
{
    echo "TEST: Check local branch $1 is checked out"
    local git_branch
    git_branch=$(git rev-parse --abbrev-ref HEAD)
    [[ "$1" = "$git_branch" ]] && echo "TEST: On correct branch: $1" || exit 1
}

test_local_branch_exists()
{
    echo "TEST: Local branch exists: $1"
    git rev-parse --quiet --verify "$1" || exit 1
}

test_no_local_branch_exists()
{
    echo "TEST: Local branch doesn't exist: $1"
    git rev-parse --quiet --verify "$1" && exit 1
}

test_remote_branch_exists()
{
    echo "TEST: Remote branch exists: $1"
    local remote_branch_count
    remote_branch_count="$(git ls-remote --heads origin $1 | wc -l | tr -d '[:space:]')"
    if [ "$remote_branch_count" -eq "0" ]; then
        exit 1
    fi
}

test_no_remote_branch_exists()
{
    echo "TEST: Remote branch doesn't exist: $1"
    local remote_branch_count
    remote_branch_count="$(git ls-remote --heads origin $1 | wc -l | tr -d '[:space:]')"
    if [ "$remote_branch_count" -eq "1" ]; then
        exit 1
    fi
}

test_tracking_branch_exists()
{
    echo "TEST: Tracking branch exists: $1"
    git config --get branch.$1.merge || exit 1
}

test_no_tracking_branch_exists()
{
    echo "TEST: Tracking branch doesn't exist: $1"
    git config --get branch.$1.merge && exit 1
}

test_branch_master()
{
    print_separator
    echo "TEST: Check current branches are on master"
    for project in "$@"
    do
    	pushd $project
        test_branch master
        popd
    done
}

test_branch_version()
{
    print_separator
    clowder forall -c 'git checkout -b v0.1'
    echo "TEST: Check current branches"
    for project in "$@"
    do
    	pushd $project
        test_branch v0.1
        popd
    done
}

test_init_herd()
{
    print_separator
    echo "TEST: Normal herd after init"
    ./clean.sh
    ./init.sh  || exit 1
    clowder herd  || exit 1
    clowder status -f || exit 1
}

test_init_herd_version()
{
    print_separator
    echo "TEST: Herd version after init"
    ./clean.sh || exit 1
    ./init.sh || exit 1
    clowder link -v v0.1 || exit 1
    clowder herd || exit 1
}

test_clowder_version()
{
    print_separator
    echo "TEST: Print clowder version"
    clowder --version || exit 1
    clowder -v || exit 1
}

test_command()
{
    print_separator
    echo "TEST: Fail with unrecognized command"
    clowder cat && exit 1
    echo "TEST: Fail with no arguments"
    clowder && exit 1
    ./clean.sh || exit 1
    echo "TEST: Fail herd with missing clowder.yaml"
    clowder herd && exit 1
}

test_save()
{
    print_separator
    echo "TEST: Fail linking a previously saved version that doesn't exist"
    clowder link -v v100 && exit 1
    echo "TEST: Fail saving a previously saved version"
    clowder save v0.1 && exit 1
    echo "TEST: Successfully save a new version"
    clowder save v0.11 || exit 1
    echo "TEST: Successfully save version with path separator in input name"
    clowder save path/separator
    clowder link -v path-separator || exit 1
    clowder herd || exit 1
    clowder status || exit 1
}

test_save_missing_directories()
{
    print_separator
    echo "TEST: Remove directories"
    rm -rf "$@"
    echo "TEST: Fail saving version with missing directories"
    clowder save missing-directories && exit 1
}

test_forall()
{
    print_separator
    CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    echo "TEST: Run forall command"
    clowder forall -c 'git status' || exit 1
    echo "TEST: Run forall script"
    clowder forall -c "$TEST_SCRIPT_DIR/test_forall_script.sh" || exit 1
    echo "TEST: Run forall command for specific groups"
    clowder forall -c 'git status' -g "$@" || exit 1
    echo "TEST: Run forall script for specific groups"
    clowder forall -c "$TEST_SCRIPT_DIR/test_forall_script.sh" -g "$@" || exit 1
    echo "TEST: Run forall command with error"
    clowder forall -c 'exit 1' && exit 1
    echo "TEST: Run forall command with --ignore-error"
    clowder forall -ic 'exit 1' || exit 1
    echo "TEST: Run forall script with error"
    clowder forall -c "$TEST_SCRIPT_DIR/test_forall_script_error.sh" && exit 1
    echo "TEST: Run forall script with --ignore-error"
    clowder forall -ic "$TEST_SCRIPT_DIR/test_forall_script_error.sh" || exit 1
}

test_forall_projects()
{
    print_separator
    echo "TEST: Run forall command for specific projects"
    clowder forall -c 'git status' -p "$@" || exit 1
    echo "TEST: Run forall script for specific projects"
    clowder forall -c "$TEST_SCRIPT_DIR/test_forall_script.sh" -p "$@" || exit 1
}

test_clean_missing_directories()
{
    rm -rf "$@"
    echo "TEST: Discard all changes when directories are missing"
    clowder clean || exit 1
    clowder status || exit 1
    clowder herd || exit 1
}

test_herd()
{
    print_separator
    echo "TEST: Successfully herd a previously saved version"
    clowder link -v v0.1 || exit 1
    clowder herd || exit 1
    echo "TEST: Successfully herd after herding a previously saved version"
    clowder link || exit 1
    clowder herd || exit 1
    echo "TEST: Remove directories"
    rm -rf "$@"
    echo "TEST: Successfully herd with missing directories"
    clowder herd || exit 1
}

test_herd_detached_heads()
{
    print_separator
    echo "TEST: Create detached HEADs"
    for project in "$@"
    do
    	pushd $project
        git checkout master~2
        popd
    done
    clowder status || exit 1
    echo "TEST: Successfully herd with detached HEADs"
    clowder herd || exit 1
}

test_herd_dirty_repos()
{
    print_separator
    make_dirty_repos "$@"
    echo "TEST: Fail herd with dirty repos"
    clowder herd && exit 1
    echo "TEST: Discard changes with clean"
    clowder clean || exit 1
    clowder status || exit 1
    echo "TEST: Successfully herd after clean"
    clowder herd || exit 1
    echo "TEST: Successfully herd twice"
    clowder herd || exit 1
}

test_herd_projects()
{
    print_separator
    echo "TEST: Successfully herd specific projects"
    clowder herd -p "$@" || exit 1
}

test_status_groups()
{
    print_separator
    echo "TEST: Test status for specific groups"
    clowder status -g "$@" || exit 1
    echo "TEST: Test status for specific groups with fetching"
    clowder status -f -g "$@" || exit 1

}

test_status_projects()
{
    print_separator
    echo "TEST: Test status for specific projects"
    clowder status -p "$@" || exit 1
    echo "TEST: Test status for specific projects with fetching"
    clowder status -f -p "$@" || exit 1
}

test_stash_missing_directories()
{
    rm -rf "$@"
    echo "TEST: Stash all changes when directories are missing"
    clowder stash || exit 1
    clowder status || exit 1
    clowder herd || exit 1
}

test_herd_groups()
{
    print_separator
    echo "TEST: Herd saved version to test herding select groups"
    clowder link -v v0.1 || exit 1
    clowder herd || exit 1
    print_separator
    echo "TEST: Herd only specific groups"
    clowder herd -g "$@" || exit 1
    clowder status || exit 1
}

print_help()
{
    print_separator
    echo "TEST: Help output"
    print_separator
    echo "TEST: clowder -h"
    clowder -h
    print_separator
    echo "TEST: clowder clean -h"
    clowder clean -h
    print_separator
    echo "TEST: clowder forall -h"
    clowder forall -h
    print_separator
    echo "TEST: clowder herd -h"
    clowder herd -h
    print_separator
    echo "TEST: clowder init -h"
    clowder init -h
    print_separator
    echo "TEST: clowder link -h"
    clowder link -h
    print_separator
    echo "TEST: clowder prune -h"
    clowder prune -h
    print_separator
    echo "TEST: clowder repo -h"
    clowder repo -h
    print_separator
    echo "TEST: clowder repo add -h"
    clowder repo add -h
    print_separator
    echo "TEST: clowder repo checkout -h"
    clowder repo checkout -h
    print_separator
    echo "TEST: clowder repo clean -h"
    clowder repo clean -h
    print_separator
    echo "TEST: clowder repo commit -h"
    clowder repo commit -h
    print_separator
    echo "TEST: clowder repo pull -h"
    clowder repo pull -h
    print_separator
    echo "TEST: clowder repo push -h"
    clowder repo push -h
    print_separator
    echo "TEST: clowder repo run -h"
    clowder repo run -h
    print_separator
    echo "TEST: clowder repo status -h"
    clowder repo status -h
    print_separator
    echo "TEST: clowder save -h"
    clowder save -h
    print_separator
    echo "TEST: clowder start -h"
    clowder start -h
    print_separator
    echo "TEST: clowder stash -h"
    clowder stash -h
    print_separator
    echo "TEST: clowder status -h"
    clowder status -h
}

print_separator()
{
    echo '--------------------------------------------------------------------------------'
}