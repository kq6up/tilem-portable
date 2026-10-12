# Packaging and GitHub preparation

The Git repository retains an unmodified TilEm 2.0 import followed by the fork
changes. Its public GitHub destination is
https://github.com/kq6up/tilem-portable, configured locally as `origin`.
Build outputs, `.deps`, `var`, app bundles and ROMs are ignored.

## Release source

Create an immutable tag after reviewing the commit, then generate the source:

```sh
git tag v2.0.4
git archive --format=tar --prefix=tilem-portable-2.0.4/ v2.0.4 | gzip -n > tilem-portable-2.0.4.tar.gz
shasum -a 256 tilem-portable-2.0.4.tar.gz
```

Publish that exact archive as a GitHub release attachment. Put its URL and
checksum into the recipe templates. Never produce a release from a recursive
copy of your working folder: it contains private dependencies and runtime files.

## Homebrew custom tap

Put `packaging/homebrew/tilibs.rb` and the completed `tilem-portable.rb.in` (renamed
`.rb`) into a separate `homebrew-tilem` repository's `Formula` directory. The
TI support library formula has a real upstream URL and SHA-256. The emulator
formula deliberately has unresolved release placeholders. Before distributing,
review inherited skin licensing and complete the GFDL license metadata with
verified provenance; the upstream README does not specify the GFDL version.

Run Homebrew's audit and installation checks on the published artifacts before
inviting users to install the tap. The formula currently installs the native
`tilem2` command plus the core and server. The local development `.app` is not a
redistributable Homebrew cask. GTK 2's planned removal also needs a maintenance
plan before proposing Homebrew/core inclusion.

## pkgsrc

Copy `packaging/pkgsrc/tilem-portable` into an appropriate pkgsrc checkout under
`emulators/tilem-portable`, rename `Makefile.in` to `Makefile` and fill the release
URLs. Run `bmake makesum`, build, install into the package staging area, generate
PLIST with pkgsrc's normal workflow, and run `pkglint`. Do not invent `distinfo`
or PLIST: both must come from the real release and installed file list on NetBSD.
The dependency buildlink files refer to the existing pkgsrc TI libraries.
Resolve inherited asset licensing before finalizing the package LICENSE.

## Slackware

Place the source release archive alongside the SlackBuild and `slack-desc`.
Install GTK 2 and the TI support library packages, then run the SlackBuild under
your normal package-build procedure. It retains its temporary build directory
and writes a `.txz`, without deleting an existing source tree. The `*_local` tag
marks a local candidate, not a SlackBuilds.org submission.

## Automation

`.github/workflows/build.yml` prepares full Linux/macOS and NetBSD GUI builds,
plus a Slackware core compilation. All four jobs passed at commit e4fff5d;
see `docs/STATUS.md` for the run and the scope of each check. A Slackware GUI
build still requires its TI library packages; use the recipe above.
A successful compile does not establish GUI operation on that OS.
