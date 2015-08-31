#! /bin/bash

# set -xv

setup_old_repos()
{
    local CLANG_DIR="$LLVM_PROJECTS_DIR/llvm/tools/clang"
    rm -rf $CLANG_DIR
    mkdir -p $CLANG_DIR
    pushd $CLANG_DIR &>/dev/null
    git clone https://github.com/JrGoodle/clang.git . &>/dev/null
    git remote remove origin &>/dev/null
    git remote add origin https://github.com/llvm-mirror/clang.git &>/dev/null
    git fetch &>/dev/null
    git branch -u origin/master &>/dev/null
    popd &>/dev/null

    local CLANG_TOOLS_EXTRA_DIR="$LLVM_PROJECTS_DIR/llvm/tools/clang/tools/extra"
    rm -rf $CLANG_TOOLS_EXTRA_DIR
    mkdir -p $CLANG_TOOLS_EXTRA_DIR
    pushd $CLANG_TOOLS_EXTRA_DIR &>/dev/null
    git clone https://github.com/JrGoodle/clang-tools-extra.git . &>/dev/null
    git remote remove origin &>/dev/null
    git remote add origin https://github.com/llvm-mirror/clang-tools-extra.git &>/dev/null
    git fetch &>/dev/null
    git branch -u origin/master &>/dev/null
    popd &>/dev/null

    local COMPILER_RT_DIR="$LLVM_PROJECTS_DIR/llvm/projects/compiler-rt"
    rm -rf $COMPILER_RT_DIR
    mkdir -p $COMPILER_RT_DIR
    pushd $COMPILER_RT_DIR &>/dev/null
    git clone https://github.com/JrGoodle/compiler-rt.git . &>/dev/null
    git remote remove origin &>/dev/null
    git remote add origin https://github.com/llvm-mirror/compiler-rt.git &>/dev/null
    git fetch &>/dev/null
    git branch -u origin/master &>/dev/null
    popd &>/dev/null

    echo ''
}

test_branch()
{
    local git_branch
    git_branch=$(git rev-parse --abbrev-ref HEAD)
    # echo "TEST: Current branch: $git_branch"
    # echo "TEST: Test branch: $1"
    [[ "$1" = "$git_branch" ]] && echo "TEST: On correct branch: $1" || exit 1
}

projects=( 'llvm' \
            'llvm/tools/clang' \
            'llvm/tools/clang/tools/extra' \
            'llvm/projects/compiler-rt' \
            'llvm/projects/libunwind' \
            'llvm/projects/dragonegg' )

export LLVM_PROJECTS_DIR="$TRAVIS_BUILD_DIR/examples/llvm-projects"
cd $LLVM_PROJECTS_DIR

echo "TEST: Golden path. Normal herd after breed"
./breed.sh && clowder herd || exit 1
echo 'TEST: Set up older copies of repos'
setup_old_repos # configure repo's for testing pulling new commits
echo "TEST: Normal herd with out of date repos"
clowder herd || exit 1
clowder meow || exit 1
echo "TEST: Successfully groom with no current changes in clowder repo"
clowder groom || exit 1
echo "TEST: Herd a previously fixed version"
clowder herd -v v0.1 || exit 1
clowder meow || exit 1

echo "TEST: Check current branches"
for project in "${projects[@]}"
do
	pushd $project &>/dev/null
    test_branch v0.1
    popd &>/dev/null
done
clowder meow || exit 1

echo "TEST: Successfully herd with no current changes"
clowder herd || exit 1
clowder meow || exit 1

echo "TEST: Check current branches"
for project in "${projects[@]}"
do
	pushd $project &>/dev/null
    test_branch master
    popd &>/dev/null
done

echo "TEST: Make dirty repos"
for project in "${projects[@]}"
do
	pushd $project &>/dev/null
    touch newfile
    git add newfile
    popd &>/dev/null
done
clowder meow || exit 1
echo "TEST: Fail herd with dirty repos"
clowder herd || exit 1
clowder meow || exit 1
echo "TEST: Discard changes with litter"
clowder litter || exit 1
clowder meow || exit 1

echo "TEST: Make dirty clowder repo"
pushd clowder &>/dev/null
touch newfile
git add newfile
popd &>/dev/null
clowder meow || exit 1

echo "TEST: Fail groom with dirty clowder repo"
clowder groom || exit 1
clowder meow || exit 1
echo "TEST: Discard changes in clowder repo"
pushd clowder &>/dev/null
git checkout -- .
popd &>/dev/null
echo "TEST: Successfully groom after discarding changes"
clowder groom || exit 1
clowder meow || exit 1

echo "TEST: Create detached HEADs"
for project in "${projects[@]}"
do
	pushd $project &>/dev/null
    git checkout master~2 &>/dev/null
    popd &>/dev/null
done
clowder meow || exit 1

echo "TEST: Successfully herd with detached HEADs"
clowder herd || exit 1
clowder meow || exit 1
echo "TEST: Herd a previously fixed version"
clowder herd -v v0.1 || exit 1
clowder meow || exit 1
echo "TEST: Normal herd after herding a previously fixed version"
clowder herd || exit 1
clowder meow || exit 1

echo "TEST: Run forall command"
clowder forall 'git status' || exit 1
echo "TEST: Fail fixing a previously fixed version"
clowder fix -v v0.1 || exit 1
echo "TEST: Successfully fix a new version"
clowder fix -v v0.11 || exit 1
clowder meow || exit 1

echo "TEST: Make dirty repos"
for project in "${projects[@]}"
do
	pushd $project &>/dev/null
    touch newfile
    git add newfile
    popd &>/dev/null
done
clowder meow || exit 1

echo "TEST: Fail herd with dirty repos"
clowder herd || exit 1
echo "TEST: Stash changes"
clowder stash || exit 1
clowder meow || exit 1

echo "TEST: Remove directories"
rm -rf 'llvm/tools/clang/tools/extra'
rm -rf 'llvm/projects/dragonegg'
echo "TEST: Herd with 2 missing directories"
clowder herd || exit 1
clowder meow || exit 1
echo "TEST: Herd fixed version to test herding select groups"
clowder herd -v v0.11 || exit 1
clowder meow || exit 1
echo "TEST: Herd only specific groups"
clowder herd -g clang llvm projects || exit 1
clowder meow || exit 1

echo ""
echo ""
echo "TEST: Help output"
echo ""
echo ""
echo "TEST: clowder -h"
clowder -h
echo ""
echo ""
echo "TEST: clowder breed -h"
clowder breed -h
echo ""
echo ""
echo "TEST: clowder herd -h"
clowder herd -h
echo ""
echo ""
echo "TEST: clowder fix -h"
clowder fix -h
echo ""
echo ""
echo "TEST: clowder forall -h"
clowder forall -h
