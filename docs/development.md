# Development

## Getting Started

Clone the repository:

```bash
$ git clone git@github.com:JrGoodle/clowder.git
$ cd clowder
```

Add the directory you cloned the repo into to `PYTHONPATH` in your shell profile. For example, if cloned into `$HOME/clowder`

```bash
export PYTHONPATH=$PYTHONPATH:$HOME/clowder
```

## Building

Install `clowder` for local development

```bash
$ script/update
```

Remove `clowder` and clean test directories

```bash
$ script/clean
```

## Testing

Run unit tests

```bash
$ script/unittests.sh
```

Run test scripts

```bash
$ script/test cats
$ script/test llvm
```

The `test_cats_*.sh` scripts can also be run individually

```bash
$ script/tests/test_cats_herd.sh
```
