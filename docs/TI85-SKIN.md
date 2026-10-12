# TI-85 keypad legends

The next 2.0.4 version adds the printed primary functions, 2nd functions, and
ALPHA letters/symbols shown in the maintainer-supplied `IMG_2157.HEIC` photograph
of a TI-85, supplied October 11, 2026. The photograph is used as a label reference
and is not redistributed. The skin remains an original vector drawing under
GPL-3.0-or-later.

## Shared labels

`server/ti85-keypad.json` contains the labels indexed by existing emulator key
names. Both `scripts/generate-ti85-skin.py` and the browser keypad read that
table. Gold labels identify 2nd functions; blue labels identify ALPHA letters
and symbols. The space symbol `␣` is used on the change-sign key.

Press 2nd or ALPHA and then the corresponding key. 2nd followed by ALPHA selects
lowercase letters, as shown by the lowercase `alpha` legend on the calculator.
The web labels describe calculator modifiers; the web keyboard shortcuts have
not been expanded to type letters automatically.

The native skin retains its 400×800 size and LCD rectangle. Its four arrows
form a directional cross matching the photograph; ALPHA, x-VAR, and DEL sit
below 2nd, EXIT, and MORE. The moved click rectangles are serialized in the
original skin-file key order so each label still sends its correct key.
The web keypad retains its existing key ordering. Existing
emulator key codes, ROM behavior, and key-binding configuration are unchanged.

## Regeneration

Run from the source checkout, with Python 3, Cairo and Pango installed:

```sh
python3 scripts/generate-ti85-skin.py
```

This updates `data/skins/ti85.svg` and the PNG embedded in `data/skins/ti85.skn`.
Pango provides font fallback for arrows, mathematical symbols, and the space
marker. Cairo and Pango are also part of the GTK dependency stack. The generated
skin files are committed, so end users do not need to regenerate them.

The browser fetches the same table from `/ti85-keypad.json`; CMake installs it
alongside the server. Non-TI-85 calculator models retain their existing labels.

## Status

The generated native artwork and a browser visual preview were reviewed.
The corrected 2.0.4 development app was built and installed on the maintainer's
Mac. The existing calculator save was backed up and matched byte-for-byte
before launch. The running native backend reports an active TI-85 LCD.
Native accessibility inspection timed out, so mouse input with the relocated
arrows and actual 2nd/ALPHA combinations still need review during use.
Version 2.0.4 is in development; no 2.0.4 release has been published.
