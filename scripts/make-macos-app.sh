#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# Creates a development app using existing dependencies, without bundling ROMs.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
case $(uname -s) in Darwin) ;; *) echo 'This script is for macOS.' >&2; exit 1;; esac
app="$root/TilEm 2.0.1.app"
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources/tilem2" "$root/var/config-201" "$root/var/run"
chmod 700 "$root/var/run"
cp "$root/build/tilem2" "$app/Contents/MacOS/TilEm.new"
mv "$app/Contents/MacOS/TilEm.new" "$app/Contents/MacOS/TilEm"
cp "$root/data/keybindings.ini" "$app/Contents/Resources/tilem2/"
cp -R "$root/data/skins" "$root/data/symbols" "$root/data/icons" "$app/Contents/Resources/tilem2/"
cat > "$app/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>TilEm 2.0.1</string>
<key>CFBundleDisplayName</key><string>TilEm 2.0.1</string>
<key>CFBundleIdentifier</key><string>org.tilem.portable.v201</string>
<key>CFBundleExecutable</key><string>TilEm</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>2.0.1</string>
<key>CFBundleVersion</key><string>2.0.1</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
# Local paths only, in a generated file ignored by Git. The ROM is never copied.
{
  printf 'XDG_CONFIG_HOME=%s\n' "$root/var/config-201"
  [ ! -f "$root/.deps/loaders.cache" ] || printf 'GDK_PIXBUF_MODULE_FILE=%s\n' "$root/.deps/loaders.cache"
  printf 'ROM=%s\n' "${TILEM_ROM:-$root/../TI85.ROM}"
  printf 'STATE_FILE=%s\n' "$root/var/config-201/calculator.sav"
  printf 'AUTOSAVE=1\n'
  printf 'CONTROL_SOCKET=%s\n' "$root/var/run/control-201.sock"
} > "$app/Contents/Resources/runtime.env"
codesign --force --sign - "$app" >/dev/null 2>&1
printf '%s\n' "$app"
