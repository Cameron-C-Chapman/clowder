# Swift `update-checkout.py`

Swift uses the [update_checkout.py](https://github.com/apple/swift/blob/master/utils/update_checkout.py) file to manage repo states. The functionality is similar to certain `clowder` commands, but is baked into the Swift repository

## Initial Checkout

### `update_checkout.py`

```bash
mkdir swift-source
cd swift-source
git clone https://github.com/apple/swift.git
./swift/utils/update-checkout --clone-with-ssh
```

### `clowder`

```bash
mkdir swift-source
cd swift-source
clowder init git@github.com:JrGoodle/swift-clowder.git
clowder herd
```

## Checkout Version

### `update_checkout.py`

```bash
swift/utils/update-checkout --scheme swift-4.0-branch --reset-to-remote --clone --clean
swift/utils/update-checkout --scheme swift-4.0-branch --match-timestamp
```

### `clowder`

```bash
clowder link -v swift-4.0-branch
clowder reset --timestamp apple/swift
```
