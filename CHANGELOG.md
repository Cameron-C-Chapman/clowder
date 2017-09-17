# 2.0.0

- Add support for uploading to PyPI as [clowder-repo](https://pypi.python.org/pypi/clowder-repo)
- Add ability to run scripts with `clowder forall`
- Print number of new local and upstream commits in output
- Add `-f` option to `clowder status` to fetch before printing status
- Add `--ignore-errors`/`-i` option to `clowder forall`
- Remove `-f` option from `clowder forall`
- Remove `-b` option from `clowder herd` (may be added back in the future)
- Add `-f` option to `clowder prune` to force delete branches

# 1.1.2

- Remove cat face emoji from command output for better portability.

# 1.1.1

- Fix bug with missing directories when running `clowder forall`.
- Fix bugs in git utilities.

# 1.1.0

- Add `clowder link` command to change `clowder.yaml` symlink location. Remove `--version` option from `clowder herd`.

# 1.0.1

- Change `clowder herd` to accept version and branch parameters.

# 1.0.0

- Add depth (`-d`) option to `clowder herd`.
- Add branch (`-b`) option to `clowder herd`.
- Add projects (`-p`) option to `clowder status`.
- Update command output formatting.

# 0.11.0

- Add various `clowder repo` subcommands:
  - `clowder repo pull`
  - `clowder repo push`
  - `clowder repo add`
  - `clowder repo commit`
  - `clowder repo status`
  - `clowder repo checkout`

# 0.10.0

- Add `depth` support to `clowder.yaml`.
- Better support for forks in `clowder.yaml`.
- Better validation of `clowder.yaml` file.
- Add `clowder prune` command.
- Add `clowder start` command.
- Add branch (`-b`) option to `clowder init`.
- Add `clowder -v` option to print version.
- More detailed git operation output.
- Rename commands:
  - `fix` -> `save`
  - `breed` -> `init`
  - `groom` -> `clean`
  - `meow` -> `status`

# 0.9.0

- Updated command output formatting.
- Remove directories when cloning fails.

# 0.8.3

- Updated `clowder forall` command output.
- Add `clowder repo` command.

# 0.8.2

- Updated command output formatting.

# 0.8.1

- Fix bug in `clowder.yaml` symlink creation.