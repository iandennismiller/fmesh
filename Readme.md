# FMesh

FMesh is a text-mode Meshtastic chat interface built with Textual supporting multiple channels.

![Screenshot](docs/screenshot.png)

## FMesh is a fork

FMesh is based on [TheCookingSenpai's eMesh](https://github.com/TheCookingSenpai/emesh) with patches from [svofski](https://github.com/svofski/fmesh).

## Installation

```bash
git clone https://github.com/iandennismiller/fmesh
cd fmesh
pip install .
```

## Quickstart

Run the following in the `fmesh` directory.

```bash
cp example-env.conf .env
fmesh-tui
```

Use ESC to exit.

Channels are numbered 0-8. To send a message to a channel, prefix the message with the number and `#`:

```txt
1# This message is being sent to channel 1.
```

We can probably do better ... but this works for now.

## Example configuration

The following example is for Linux.
To run on MacOS instead, uncomment that line.

```ini
# linux
FMESH_DEVICE=/dev/ttyUSB0

# macos
# FMESH_DEVICE=/dev/cu.usbserial-0001

# channel to start on by default
FMESH_CHANNEL=0
```

### License

[MIT License](License.md)
