#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
exec python3 "$root/server/server.py" --socket "$root/var/run/control-201.sock" \
  --program-dir "$root/var/toys/sunstar" "$@"
