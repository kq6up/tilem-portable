#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Build pinned upstream TI libraries locally. No system installation or sudo.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
revision=6dba390e7390c4b98ae96287b39a3971c331fbef
sha=c6c37882b73e86d6bee6f9b253976479491ab4956fbf5e556e3a585c66c94a50
prefix=${TILEM_DEPS_PREFIX:-$root/.deps/prefix}
mkdir -p "$root/.deps/downloads" "$root/.deps/src"
archive="$root/.deps/downloads/tilibs-$revision.tar.gz"
if [ ! -f "$archive" ]; then
  curl --fail --location --retry 3 "https://codeload.github.com/debrouxl/tilibs/tar.gz/$revision" -o "$archive"
fi
if command -v sha256sum >/dev/null 2>&1; then
  actual=$(sha256sum "$archive" | awk '{print $1}')
elif command -v sha256 >/dev/null 2>&1; then
  actual=$(sha256 -q "$archive")
else
  actual=$(shasum -a 256 "$archive" | awk '{print $1}')
fi
[ "$actual" = "$sha" ] || { echo 'TI library archive checksum mismatch' >&2; exit 1; }
source="$root/.deps/src/tilibs-$revision"
[ -d "$source" ] || tar -xzf "$archive" -C "$root/.deps/src"
[ ! -f "$root/.deps/env.sh" ] || . "$root/.deps/env.sh"
cmake -S "$source" -B "$root/.deps/build-tilibs" \
  -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=OFF -DCMAKE_INSTALL_PREFIX="$prefix" "$@"
cmake --build "$root/.deps/build-tilibs" --parallel "${TILEM_JOBS:-2}"
cmake --install "$root/.deps/build-tilibs"
printf '\nFor the TilEm build, set:\nexport PKG_CONFIG_PATH="%s/lib/pkgconfig:%s/lib64/pkgconfig${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"\n' "$prefix" "$prefix"
