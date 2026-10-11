#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
# An optional private environment can select project-local dependencies.
[ ! -f .deps/env.sh ] || . .deps/env.sh
cmake -S . -B "${TILEM_BUILD_DIR:-build}" -DCMAKE_BUILD_TYPE=Release "$@"
cmake --build "${TILEM_BUILD_DIR:-build}" --parallel "${TILEM_JOBS:-2}"
