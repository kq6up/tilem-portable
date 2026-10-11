# Licensing

TilEm is free software. Preserve the original authors and notices when sharing
this fork and provide the corresponding source under the applicable licenses.

* The native GUI and debugger are primarily GPL-3.0-or-later (`COPYING`).
* The emulator core in `emu/` is LGPL-2.1-or-later (`COPYING.LESSER`).
* The new bridge and core runtime use LGPL-2.1-or-later. New CLI, server,
  build scripts, ASCII85P converter and TI-85 vector skin use GPL-3.0-or-later.
* Some inherited GUI files have GPL-2.0-or-later notices. Those notices remain.
* Inherited skin images have individual provenance and licenses: see
  `data/skins/README`. Several are described upstream as GFDL; others as GPL
  or LGPL. These assets are not all covered by the GUI's license. Review the
  original image attribution and license obligations before a binary release.
* TI support libraries retain their upstream licenses and are separate
  dependencies; this repository does not vendor their source or binaries.

Calculator ROMs are separate copyrighted material. No ROM is included in the
repository, app bundle or release archive. Supply a ROM you are entitled to use.

The locally supplied SUN/STAR toy is kept under the ignored `var/toys/` directory.
It has no explicit redistribution license in the supplied archive and is not
included in public source archives. Its documentation and accuracy claims belong
to its author, not to the emulator project.
