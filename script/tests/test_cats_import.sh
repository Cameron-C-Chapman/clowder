#!/usr/bin/env bash

cd "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )" || exit 1

. test_utilities.sh
prepare_cats_example
cd "$CATS_EXAMPLE_DIR" || exit 1

export all_projects=( 'mu' 'duke' \
                      'black-cats/kit' \
                      'black-cats/kishka' \
                      'black-cats/sasha' \
                      'black-cats/jules' )

export black_cats_projects=( 'black-cats/kit' \
                             'black-cats/kishka' \
                             'black-cats/sasha' \
                             'black-cats/jules' )

test_cats_default_herd_branches() {
    for project in "${black_cats_projects[@]}"; do
    	pushd $project
        test_branch master
        popd
    done
    pushd mu
    test_branch knead
    popd
    pushd duke
    test_branch purr
    popd
}

print_double_separator
echo "TEST: Test clowder file with import"

test_clowder_import_default() {
    print_single_separator
    echo "TEST: Test clowder file with default import"

    clowder link || exit 1
    clowder herd || exit 1
    clowder link -v import-default || exit 1
    clowder herd || exit 1
    clowder status || exit 1

    for project in "${black_cats_projects[@]}"; do
        pushd $project
        test_branch import-default
        popd
    done
}
test_clowder_import_default

test_clowder_import_version() {
    print_single_separator
    echo "TEST: Test clowder file with version import"
    clowder link || exit 1
    clowder herd || exit 1
    clowder link -v import-version || exit 1
    clowder herd || exit 1
    clowder status || exit 1

    for project in "${black_cats_projects[@]}"; do
        pushd $project
        test_branch import-version
        popd
    done
}
test_clowder_import_version

test_clowder_import_override_group_ref() {
    print_single_separator
    echo "TEST: Test clowder file import overriding group ref"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-override-group-ref || exit 1
    clowder herd || exit 1
    for project in "${black_cats_projects[@]}"; do
    	pushd $project
        test_branch import-group-branch
        popd
    done
    pushd mu
    test_branch knead
    popd
    pushd duke
    test_branch purr
    popd
}
test_clowder_import_override_group_ref

test_clowder_import_override_project_ref() {
    print_single_separator
    echo "TEST: Test clowder file import overriding project ref"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-project-ref || exit 1
    clowder herd || exit 1
    for project in "${all_projects[@]}"; do
    	pushd $project
        test_branch master
        popd
    done
}
test_clowder_import_override_project_ref

test_clowder_import_add_project_to_group() {
    print_single_separator
    echo "TEST: Test clowder file import adding new project to existing group"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-add-project-to-group || exit 1
    clowder herd -g cats || exit 1
    test_cats_default_herd_branches
    pushd ash
    test_branch master
    popd
    rm -rf ash || exit 1
}
test_clowder_import_add_project_to_group

test_clowder_import_add_new_group() {
    print_single_separator
    echo "TEST: Test clowder file import adding new group"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-add-group || exit 1
    clowder herd -g rip || exit 1
    test_cats_default_herd_branches
    pushd ash
    test_branch master
    popd
    rm -rf ash || exit 1
}
test_clowder_import_add_new_group

test_clowder_import_recursive_override_project_ref() {
    print_single_separator
    echo "TEST: Test clowder file recursive import overriding project ref"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-recursive-project-ref || exit 1
    clowder herd || exit 1
    for project in "${black_cats_projects[@]}"; do
    	pushd $project
        test_branch master
        popd
    done
    pushd mu
    test_branch recursive-import
    popd
    pushd duke
    test_branch purr
    popd
}
test_clowder_import_recursive_override_project_ref

test_clowder_import_recursive_add_project_to_group() {
    print_single_separator
    echo "TEST: Test clowder file recursive import adding new project to existing group"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-recursive-add-project-to-group || exit 1
    clowder herd -g cats || exit 1
    test_cats_default_herd_branches
    pushd ash
    test_branch recursive-import
    popd
    rm -rf ash || exit 1
}
test_clowder_import_recursive_add_project_to_group

test_clowder_import_recursive_add_new_group() {
    print_single_separator
    echo "TEST: Test clowder file recursive import adding new group"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-recursive-add-group || exit 1
    clowder herd -g rip || exit 1
    test_cats_default_herd_branches
    pushd ash
    test_branch recursive-import
    popd
    rm -rf ash || exit 1
}
test_clowder_import_recursive_add_new_group

test_clowder_import_recursive_override_default() {
    print_single_separator
    echo "TEST: Test clowder file recursive import overriding default"
    clowder link || exit 1
    clowder herd || exit 1
    test_cats_default_herd_branches
    clowder link -v import-recursive-default || exit 1
    clowder herd || exit 1
    for project in "${black_cats_projects[@]}"; do
    	pushd $project
        test_branch recursive-import
        popd
    done
    pushd mu
    test_branch knead
    popd
    pushd duke
    test_branch purr
    popd
}
test_clowder_import_recursive_override_default