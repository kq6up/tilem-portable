#!/bin/sh
# SPDX-License-Identifier: GPL-3.0-or-later
# For the ephemeral NetBSD 10.1 amd64 CI VM, which omits the native X11 sets.
set -eu
[ "$(uname -s)" = NetBSD ] && [ "$(uname -m)" = amd64 ]
case "$(uname -r)" in
  10.1*) ;;
  *) echo 'This CI dependency script requires NetBSD 10.1.' >&2; exit 1 ;;
esac

task_dir=$(mktemp -d)
trap 'rm -rf "$task_dir"' EXIT HUP INT TERM
sets_url=https://archive.netbsd.org/pub/NetBSD-archive/NetBSD-10.1/amd64/binary/sets
# Digests from the official release SHA512 file. Verify before extracting as root.
for set_name in xbase xcomp; do
  case "$set_name" in
    xbase) expected=b6ac2195f91d7ae395ec2734c9ae2a4727014629fbdc94562531225e0d51e3b2705047e8440fcf75e1dacdcecb3cb980df7a82f838c12ad5274ba8ce95e49b72 ;;
    xcomp) expected=40ef5271cbfcc7fce1bdbbd12217521b79cc074b9b05831184e941dd40d4db867afae7684c179a512c327eeee6cd8d4fd7daff86b5da3bbdfcc763910271dc68 ;;
  esac
  archive="$task_dir/$set_name.tar.xz"
  ftp -o "$archive" "$sets_url/$set_name.tar.xz"
  actual=$(sha512 -q "$archive")
  if [ "$actual" != "$expected" ]; then
    echo "Checksum mismatch for $set_name.tar.xz" >&2
    exit 1
  fi
  tar -xpf "$archive" -C /
done

/usr/sbin/pkg_add -u cmake pkgconf 'gtk2+' libticalcs2
