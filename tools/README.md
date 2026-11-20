# oxtool

`oxtool` is Oxyde's command-line toolkit. The binary ships with each
[Release](../../releases) (`oxtool` for Linux, `oxtool.exe` for Windows); put it
next to the `oxyde` engine binary.

Run `oxtool --help` for the full list. The headline commands:

| Command | What it does |
|---------|--------------|
| `oxtool fuse …` | Convert MUGEN/Ikemen characters to Oxyde's FUSE format, with a fidelity `--verify`. |
| `oxtool audit <def>` | Report how much of a character actually works, move by move. |
| `oxtool moves --try <def>` | Perform each move headlessly and report whether it fires and connects. |
| `oxtool sprites …` | Decode, export, re-pack and (`--png8`) shrink SFF sprite banks; build HD sidecars. |
| `oxtool shot <root> <screen>` | Render any game screen to a PNG, headlessly — title, select, stage-select, a fight. |
| `oxtool docs <root>` | Re-derive and check every number and claim in the documentation. |

See `docs/IMPORT-PIPELINE.md`, `docs/FUSE-CONVERSION.md`, `docs/DIAGNOSTICS.md`
and `docs/HD-SPRITES.md` for the workflows these fit into.
