# FMesh

FMesh is a text-mode Meshtastic chat interface built with Textual supporting multiple channels.

FMesh is based on [TheCookingSenpai's eMesh](https://github.com/TheCookingSenpai/emesh) with patches from [svofski](https://github.com/svofski/fmesh).

## Installation

```bash
git clone https://github.com/iandennismiller/fmesh
pip install .
```

## Usage

```bash
fmesh-tui
```

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
