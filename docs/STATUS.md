# Build and runtime status — 2026-10-11

## Completed on this machine

* Source published to https://github.com/kq6up/tilem-portable, preserving the
  original import and development commit history.
* The 2.0.1 source release was published before integrating the Linux fix:
  https://github.com/kq6up/tilem-portable/releases/tag/v2.0.1. It includes the
  source gzip and SHA256SUMS.txt, tagged at commit b371fdda.
* Original TilEm 2.0 imported into a local Git repository in Downloads.
* CMake core, shared bridge, CLI and full GTK GUI compiled with AppleClang 21
  on Apple Silicon macOS, using project-local GTK/TI dependencies and existing
  Homebrew libraries.
* CMake installation staged successfully under `_install`.
* Native app launched through Finder. A missing key bindings resource path was
  corrected in `gui/files.c`; the corrected GUI runs.
* The loopback server attached to the very same GTK calculator via its socket.
  Pressing ON, CLEAR, 2, +, 2 and ENTER displayed `2+2` and `4` on its real LCD.
* Existing ROM-independent core checks passed during the initial core build.
* Added an original TI-85 native keypad skin with 50 clickable keys. It is
  generated from code; no calculator photograph or ROM is redistributed.
* Converted the locally supplied SUN.ASC and STAR.ASC into tokenized .85p files.
  Both transferred successfully through the native GUI's link support and appear
  in its program menu. SUN runs on the emulated TI-85. The supplied
  2026-08-29 16:15:53 example displayed GHA 63.449, Dec 9.109 and SD 15.8.
  This reproduces one example; it does not establish almanac accuracy generally.
* The updated app is named `TilEm 2.0.1.app`, with a distinct application identity
  and `var/run/control-201.sock`, to avoid reconnecting to an older GTK process
  that remained running. The browser panel is attached to the updated app.

* Corrected STAR's Goto destination cache. The corrected native run selected
  Alpheratz and accepted 2026-10-11 12:00 UT; it displayed GHA Aries 200.057,
  SHA 357.329 and Dec 29.145. This confirms execution, not astronomical accuracy.
* Web buttons remain usable during transfers: F2 selected OVERW on the actual
  duplicate STAR prompt and the transfer completed successfully.
* Forced-quit recovery now probes an existing owned Unix socket and removes it
  only when it is stale. The macOS app always requests control on startup;
  reopening through Finder reconnected the native GUI and browser successfully.

* Fixed the native keypad background's initial draw at the skin's exact size.
  The app was rebuilt and restarted; the user confirmed the corrected appearance.

* Enabled automatic state saves for the macOS development app, using the
  private `var/config-201/calculator.sav`. Native launches can opt in with
  `--autosave`; `--no-autosave` disables it. Saves run every 30 seconds when
  no link task is active, after successful web transfers, and on normal exit.
  State writes use a private sibling file and atomic replacement.
* Reloaded SUN and STAR, closed the updated app normally, and reopened it.
  Both remained in its program menu; STAR ran from the restored calculator RAM.
* The private STAR copy retains two result pages. The last page now shows GHA
  star and declination. For Alpheratz at 2026-10-11 12:00 UT the actual LCD
  displayed 197.386 and 29.145 in DDD.MMm; the user confirmed the presentation.
  Its existing decimal-degree modulo-360 calculation is retained.

## Linux build evidence reported by Claude (2.0.2)

The following results were reported in the maintainer-supplied Claude build
notes and patch dated October 11, 2026. They were not independently rerun on
this macOS machine when integrating the patch.

* Ubuntu 24.04 (GCC 13.3, GTK 2.24.33): the GUI, core, bridge and headless tool
  build with `scripts/build.sh -DBUILD_TESTING=OFF`. The GUI ran under Xvfb with
  `-m ti85 --control-socket`, booted a TI-85 ROM, accepted key presses, returned
  the LCD and received programs. 2.0.1 failed to link here: `S_ISSOCK` in
  `gui/control.c` was hidden by strict C99; CMake now defines `_DEFAULT_SOURCE`
  for the GUI on Linux only.
* Link transfers depend on the TI library version. With Ubuntu 24.04's packaged
  libticalcs 1.1.10 (2023-11-26 snapshot) a 148-byte program transferred, but
  every program tried with 384 or more data bytes failed on the calculator with
  `ERROR 35 LINK TRANSMISSION ERROR`. Built against the tilibs revision pinned in
  `scripts/bootstrap-tilibs.sh`, all of them transferred. Use the pinned
  libraries on Linux if you send programs.
* The new `_DEFAULT_SOURCE` definition is limited to the Linux GUI target.
  The macOS app name, bundle identifier, control socket, and saved-state directory
  remain at their existing 2.0.1 identities so this source update does not point
  the launcher at a different calculator save. A macOS rebuild of 2.0.2 is
  recorded below; the earlier GUI runtime evidence above is for 2.0.1.

## Slackware build and runtime verified (2.0.2)

* Built on the maintainer's ARM64 Slackware 15.0+ system over SSH:
  Linux 6.18.52-armv8, GCC 16.2.0, CMake 4.4.3, GTK 2.24.33, and GLib 2.90.0.
  `scripts/bootstrap-tilibs.sh` built the pinned TI libraries under the checkout's
  private `.deps/prefix`; no system packages were replaced. The GUI, core,
  shared bridge, and headless tool compiled, and installation staged privately.
* Ran the real GTK GUI under Xvfb with the TI-85 vector skin and the maintainer's
  ROM. The native control socket returned the actual 128x64 LCD and keys;
  pressing ON, CLEAR, 2, +, 2, ENTER displayed 4.
* Built TI85Nav's supplied `tools/ascii85p.c` with the Slackware C99 compiler.
  It packed all eight supplied navigation sources and passed its own file
  structure/checksum checks. Its five main programs (SETUP, SIGHT, MOON, STAR,
  and SUN) all transferred through the native link with the pinned TI libraries
  and completed without ERROR 35. This does not identify every possible cause
  of ERROR 35; malformed program encoding remains a separate possibility.
* SETUP stored the position and weather defaults. MOON at 2026-10-11 16:00 UTC
  displayed GHA 53.389 and declination -15.478 in DDD.MMm, HP 56.2 minutes, and
  SD 15.3 minutes. SUN's supplied 2026-08-29 16:15:53 UTC example displayed
  GHA 63.449, declination 9.109, and SD 15.8. SIGHT's recorded first Moon case
  completed all three result pages with an intercept of 1.9995632127 NM.
* STAR selected Alpheratz at 2026-10-11 12:00 UTC and displayed GHA Aries
  200.057, SHA 357.329, and declination 29.145 in DDD.MMm. Its final page
  displayed GHA star 197.386 and declination 29.145. These are program execution
  checks against the recorded examples, not a new general almanac accuracy study.
* This confirms the GTK runtime under a virtual X display and native socket
  transfers on this ARM64 Slackware system. Physical USB cables and operation
  on the user's visible desktop were not exercised. AIR, SEA, and HO229 were
  packed and structurally checked; their runtime was not checked in this pass.

## macOS rebuild and CI setup (2.0.2)

* Recompiled the native GUI, core, and bridge successfully on this Apple Silicon
  Mac with `scripts/build.sh -DBUILD_TESTING=OFF`. The installed development app
  was not replaced or restarted during this build, preserving its live session.
* The first automatic CI run of the Linux patch exposed setup problems:
  Homebrew's keg-only libarchive was missing from `PKG_CONFIG_PATH`, the
  Slackware container lacked liblz4, and the NetBSD job used `gtk2` instead of
  the binary package name `gtk2+` and encountered existing dependency versions.
  The workflow now includes the missing paths/packages and uses `pkg_add -u`.
  Matrix jobs no longer cancel each other on the first failure. These changes
  do not constitute a completed NetBSD build.

## Still pending

* NetBSD native builds/GUI operation and the Slackware 15.0 x86 container build
  remain to be confirmed. The ARM64 Slackware build/runtime is recorded above.
* Package review/acceptance and Homebrew audit/installation are not performed.
  Recipe release placeholders and inherited GFDL image
  provenance must be resolved before submission.
* The macOS development app uses local dependencies and is not a self-contained,
  signed distribution. GTK 2 deprecation requires a longer-term GUI maintenance
  plan.
