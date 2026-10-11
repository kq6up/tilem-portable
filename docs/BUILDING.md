# Build instructions

## Common build

A C99 compiler, CMake 3.16+, pkg-config and standard math library build the core.
The default GUI additionally needs GTK 2.6+, GLib 2.32+, and all four TI library
pkg-config modules: `ticonv`, `tifiles2`, `ticables2`, `ticalcs2`.
Use a single prefix/toolchain for dependencies. Python 3.8+ runs the optional
server and source converter; it is not required to run the native GUI.

```sh
scripts/build.sh -DCMAKE_INSTALL_PREFIX=/usr/local -DBUILD_TESTING=OFF
# Staging for a package, without writing the system prefix:
DESTDIR="$PWD/stage" cmake --install build
```

Use `TILEM_BUILD_DIR=build-core scripts/build.sh -DTILEM_BUILD_GTK=OFF` for a
separate core-only build. This requires no GTK or TI link libraries.
The original autotools build is retained; CMake is the maintained portable path.
The control socket currently targets Unix systems, including all three requested
platforms. Windows is outside this fork's current build target set.

## macOS / Homebrew

Install Xcode Command Line Tools and the dependencies you choose to install:

```sh
brew install cmake pkgconf gtk+ glib libusb libarchive
scripts/bootstrap-tilibs.sh -DCMAKE_PREFIX_PATH="$(brew --prefix)"
export PKG_CONFIG_PATH="$PWD/.deps/prefix/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
scripts/build.sh -DCMAKE_PREFIX_PATH="$(brew --prefix)" -DBUILD_TESTING=OFF
TILEM_ROM=/path/to/TI85.ROM scripts/make-macos-app.sh
```

GTK 2 is the `gtk+` formula; `gtk+3` is not a drop-in replacement. The TI libraries
were not present in Homebrew/core when inspected on 2026-10-11. The bootstrap
script downloads a checksummed, pinned commit from the upstream tilibs project
and installs all four libraries into `.deps/prefix`, without sudo. It can be
rerun and accepts additional CMake options. Its sources are separate dependencies.

Homebrew marks GTK 2 deprecated, with planned disablement in 2027. A future
Homebrew/core submission will need a maintained GUI dependency or another
approved packaging solution. The included custom tap candidates are a first step.

On this local machine, missing GTK runtime bottles were extracted, checksummed
and relocated into `.deps` while reusing existing Homebrew dependencies. No
system Homebrew packages were installed. That generated `.deps/env.sh` selects
this private environment automatically in `scripts/build.sh`. It is not tracked
or portable: a fresh checkout should use the normal dependency steps above.

Open the app in Finder/LaunchServices. Direct launching from a restricted
headless sandbox cannot initialize Quartz screens. Moving the development app or
its private dependencies requires rebuilding it. The app does not contain a ROM.

## Debian / Ubuntu

```sh
sudo apt-get install cmake pkg-config libgtk2.0-dev libusb-1.0-0-dev \
  libticalcs-dev libticables-dev libtifiles-dev libticonv-dev
scripts/build.sh -DBUILD_TESTING=OFF
```

`libusb-1.0-0-dev` is needed because the packaged `ticables2.pc` requires it.
The packaged TI libraries are enough to build and run, but program transfers
larger than a few hundred bytes failed with them on Ubuntu 24.04 (see
[status](STATUS.md)). For working transfers also install `libarchive-dev`, run
`scripts/bootstrap-tilibs.sh`, and export the `PKG_CONFIG_PATH` it prints before
building. A headless start needs `-m ti85` (or the right model) so the
model-selection dialog does not appear.

## Slackware

Use a full Slackware installation with the development tools, CMake, GTK 2,
GLib, pkg-config, libusb and libarchive. SlackBuilds.org supplies the TI library
chain (`libticonv`, `libtifiles2`, `libticables2`, then `libticalcs2`) and an
upstream `tilem2` package. This fork uses package name `tilem-portable`.

With the four libraries installed through the package manager:

```sh
pkg-config --modversion gtk+-2.0 ticonv tifiles2 ticables2 ticalcs2
scripts/build.sh -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib64 -DBUILD_TESTING=OFF
```

Alternatively, use `scripts/bootstrap-tilibs.sh` for private TI dependencies,
then add `.deps/prefix/lib/pkgconfig` (and `lib64/pkgconfig`, if used) to
`PKG_CONFIG_PATH`. See the SlackBuild candidate under `packaging/slackware`.
Use an X session for the native GTK GUI.

## NetBSD / pkgsrc

Install CMake, pkgconf, GTK 2 and `libticalcs2` from the same pkgsrc branch and
ABI. The latter depends on the other three TI libraries. Python is optional.
For example, with binary package administration privileges:

```sh
pkg_add cmake pkgconf gtk2 libticalcs2 python313
export PATH="/usr/pkg/bin:$PATH"
export PKG_CONFIG_PATH="/usr/pkg/lib/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"
scripts/build.sh -DCMAKE_PREFIX_PATH=/usr/pkg -DCMAKE_INSTALL_PREFIX=/usr/pkg -DBUILD_TESTING=OFF
```

Package names and the Python version depend on your configured repository.
For source packaging, see `packaging/pkgsrc/tilem-portable/Makefile.in` and
`docs/PACKAGING.md`. Prefer pkgsrc's TI libraries here: upstream tilibs' current
CMake file treats every non-Apple Unix as Linux and has not been confirmed on
NetBSD. An X session is needed for GTK 2 on NetBSD.

## Optional checks

Existing ROM-independent core checks can be enabled with `-DBUILD_TESTING=ON`
and run using `ctest --test-dir build --output-on-failure`. Never put a
proprietary ROM into CI, a source archive, or a Git repository.
