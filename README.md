# TilEm Portable

A portable fork of **TilEm 2.0**, the TI graphing calculator emulator, retaining
its native GTK calculator GUI, debugger, link transfers and original authorship.
The new CMake build targets macOS, Slackware Linux and NetBSD/pkgsrc.

Additional tools provide local automation of **the same calculator shown in the
native window**: press/release every key, read its actual LCD and send programs.
Python is only needed for the optional HTTP control server and conversion tools.
There is also a standalone core and command line LCD capture tool.

## Build the native GUI

Requirements: C99 compiler, CMake 3.16+, pkg-config, GTK 2, GLib 2.32+, and
`ticalcs2`, `ticables2`, `tifiles2`, `ticonv`. Supply your own calculator ROM.

```sh
scripts/build.sh -DCMAKE_INSTALL_PREFIX="$PWD/_install"
cmake --install build
_install/bin/tilem2 -r /path/to/TI85.ROM
```

On macOS, GTK 2 uses Homebrew's Quartz backend. The development app can be
created with `TILEM_ROM=/path/to/TI85.ROM scripts/make-macos-app.sh`, then opened
in Finder. It contains the real compiled GUI and its resources. It uses existing
runtime libraries and is not a self-contained distributable app.

[Building](docs/BUILDING.md) covers Homebrew, Slackware and NetBSD.
[Packaging](docs/PACKAGING.md) includes candidate tap, pkgsrc and SlackBuild
recipes. [Current build evidence](docs/STATUS.md) distinguishes completed work
from platforms that still need an actual build.

## Optional access for tools and agents

Start the native GUI with an opt-in Unix socket, then attach the HTTP server:

```sh
mkdir -p var/run
chmod 700 var/run
build/tilem2 -r /path/to/TI85.ROM --control-socket "$PWD/var/run/control.sock"
# In another terminal:
python3 server/server.py --socket "$PWD/var/run/control.sock" --port 8865
```

Open **http://127.0.0.1:8865** for the secondary control panel. The native GUI
remains the main user interface. The socket has mode 0600; HTTP listens only on
loopback. No account, cloud service or external Python packages are needed.

* `GET /api/state`: actual model, keys, PC, LCD state and base64 one-byte pixels.
* `GET /screen.png`: the current LCD as a PNG.
* `POST /api/key`: `{"key":"Enter","action":"tap","hold_ms":120}`.
  `down` and `up` allow chords. Key names come from the calculator model.
* `POST /api/release`: `{}` releases every key.
* `POST /api/reset`: `{}` power cycles the emulator.
* Add `--program-dir /path/to/programs` to enable `GET /api/programs` and
  `POST /api/send` with `{"file":"SUN.85p"}`. This queues a real native link
  transfer. Poll `state.transfer.status` for `done` or `error`. An accepted
  request is not yet a completed transfer. Sending is disabled without that
  directory and is limited to `.85p` basenames inside it. Keys remain available
  while sending so the calculator's OVERW/RENAME/SKIP prompts can be answered.

The native socket itself is a local user API, accepting `state`, `key CODE 0|1`,
`reset`, `shutdown` (close the native window when no transfer is active),
and `send BASE64_ABSOLUTE_PATH`, one newline-terminated command per
connection. Do not expose either endpoint to a network proxy.

For a separate calculator without GTK:

```sh
scripts/build.sh -DTILEM_BUILD_GTK=OFF
build/tilem-headless /path/to/TI85.ROM 1000 screen.pbm
python3 server/server.py --rom /path/to/TI85.ROM
```

The standalone backend does not provide link transfers.

## ASCII85P BASIC sources

```sh
python3 scripts/ascii85p.py SUN.ASC STAR.ASC --output-dir programs
```

This converter implements the documented TI-85 token and file formats for a
subset of BASIC, including the constructs in the supplied SUN/STAR toy. It
rejects unsupported syntax, rather than silently converting it. It does not
execute source files on the host. Use the GUI's **Send File** command or the
optional server to transfer the resulting `.85p` files.

## License and source publication

The GUI is primarily **GPL-3.0-or-later** and the core is **LGPL-2.1-or-later**.
Preserve the original file notices and the individually licensed skin assets.
See [licensing](docs/LICENSING.md), `COPYING`, `COPYING.LESSER` and the retained
upstream `README`. ROMs, local dependencies, app bundles, calculator saves and
locally supplied toy files are excluded from Git and source release archives.

The repository starts with an unmodified TilEm 2.0 import. No remote is
configured. After reviewing the changes, create your GitHub repository and push
`main`. Packaging recipes require its real release URL and checksum before use.
