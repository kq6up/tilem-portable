# Build and runtime status — 2026-10-11

## Completed on this machine

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

## Still pending

* Slackware and NetBSD native builds and GUI operation remain unverified.
  Build instructions, candidate recipes and build-only CI are prepared.
* GitHub publication, package review/acceptance and Homebrew audit/installation
  are not performed. Recipe release placeholders and inherited GFDL image
  provenance must be resolved before submission.
* The macOS development app uses local dependencies and is not a self-contained,
  signed distribution. GTK 2 deprecation requires a longer-term GUI maintenance
  plan.
