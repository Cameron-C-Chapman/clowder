#!/usr/bin/env bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" || exit 1

. test_utilities.sh

export black_cats_projects=( 'black-cats/kit' \
                             'black-cats/kishka' \
                             'black-cats/sasha' \
                             'black-cats/jules' )

export all_projects=( 'mu' 'duke' \
                      'black-cats/kit' \
                      'black-cats/kishka' \
                      'black-cats/sasha' \
                      'black-cats/jules' )

prepare_cats_example
cd "$CATS_EXAMPLE_DIR" || exit 1

print_double_separator
echo "TEST: Test clowder start"

test_start() {
    print_single_separator
    echo "TEST: Start new branch"

    clowder herd || exit 1
    clowder start start_branch -g cats || exit 1

    pushd mu
    test_branch start_branch
    test_no_remote_branch_exists start_branch
    popd
    pushd duke
    test_branch start_branch
    test_no_remote_branch_exists start_branch
    popd
    for project in "${black_cats_projects[@]}"; do
    	pushd $project
        test_branch master
        test_no_remote_branch_exists start_branch
        test_no_local_branch_exists start_branch
        popd
    done

    clowder start start_branch || exit 1

    for project in "${all_projects[@]}"; do
    	pushd $project
        test_branch start_branch
        test_no_remote_branch_exists start_branch
        popd
    done
}
test_start

if [ -z "$TRAVIS_OS_NAME" ]; then
    test_start_tracking() {
        print_single_separator
        echo "TEST: Test start tracking branch"
        clowder herd || exit 1

        echo "TEST: No local or remote branches"
        clowder prune -af tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
        	pushd $project
            test_no_remote_branch_exists tracking_branch
            test_no_local_branch_exists tracking_branch
            popd
        done

        clowder start -t tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
        	pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_tracking_branch_exists tracking_branch
            popd
        done

        echo "TEST: Existing local branch checked out, remote tracking branch exists"
        clowder prune -af tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
        	pushd $project
            test_no_remote_branch_exists tracking_branch
            test_no_local_branch_exists tracking_branch
            popd
        done

        clowder start -t tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_tracking_branch_exists tracking_branch
            popd
        done

        clowder start -t tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_tracking_branch_exists tracking_branch
            popd
        done

        echo "TEST: Existing local branch not checked out, remote tracking branch exists"
        clowder prune -af tracking_branch || exit 1
        clowder start -t tracking_branch || exit 1
        clowder forall -c 'git checkout master' || exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch 'master'
            test_remote_branch_exists tracking_branch
            test_tracking_branch_exists tracking_branch
            popd
        done

        clowder start -t tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_tracking_branch_exists tracking_branch
            popd
        done

        echo "TEST: No local branch, existing remote branch"
        clowder prune -af tracking_branch || exit 1
        clowder start -t tracking_branch || exit 1
        clowder prune -f tracking_branch || exit 1

        pushd mu
        test_branch knead
        test_remote_branch_exists tracking_branch
        test_no_local_branch_exists tracking_branch
        popd
        pushd duke
        test_branch purr
        test_remote_branch_exists tracking_branch
        test_no_local_branch_exists tracking_branch
        popd
        for project in "${black_cats_projects[@]}"; do
            pushd $project
            test_branch 'master'
            test_remote_branch_exists tracking_branch
            test_no_local_branch_exists tracking_branch
            popd
        done

        clowder start -t tracking_branch && exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_remote_branch_exists tracking_branch
            test_no_tracking_branch_exists tracking_branch
            popd
        done

        echo "TEST: Existing local branch checked out, existing remote branch, no tracking relationship"
        clowder prune -af tracking_branch || exit 1
        clowder start -t tracking_branch || exit 1
        clowder prune -f tracking_branch || exit 1
        clowder forall -c 'git checkout -b tracking_branch' || exit 1
        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_no_tracking_branch_exists tracking_branch
            popd
        done
        clowder start -t tracking_branch && exit 1
        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_no_tracking_branch_exists tracking_branch
            popd
        done

        echo "TEST: Existing local branch not checked out, existing remote branch, no tracking relationship"
        clowder prune -af tracking_branch || exit 1
        clowder start -t tracking_branch || exit 1
        clowder prune -f tracking_branch || exit 1
        clowder forall -c 'git checkout -b tracking_branch' || exit 1
        clowder forall -c 'git checkout master' || exit 1
        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch 'master'
            test_local_branch_exists tracking_branch
            test_remote_branch_exists tracking_branch
            test_no_tracking_branch_exists tracking_branch
            popd
        done
        clowder start -t tracking_branch && exit 1
        for project in "${all_projects[@]}"; do
            pushd $project
            test_local_branch_exists tracking_branch
            test_remote_branch_exists tracking_branch
            test_no_tracking_branch_exists tracking_branch
            popd
        done

        echo "TEST: Existing local branch checked out, no remote branch"
        clowder prune -af tracking_branch
        clowder start tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_local_branch_exists tracking_branch
            test_no_remote_branch_exists tracking_branch
            popd
        done

        clowder start -t tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_tracking_branch_exists tracking_branch
            popd
        done

        echo "TEST: Existing local branch not checked out, no remote branch"
        clowder prune -r tracking_branch >/dev/null
        clowder start tracking_branch || exit 1
        clowder forall -c 'git checkout master'

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch 'master'
            test_local_branch_exists tracking_branch
            test_no_remote_branch_exists tracking_branch
            popd
        done

        clowder start -t tracking_branch || exit 1

        for project in "${all_projects[@]}"; do
            pushd $project
            test_branch tracking_branch
            test_remote_branch_exists tracking_branch
            test_tracking_branch_exists tracking_branch
            popd
        done
    }
    test_start_tracking
fi