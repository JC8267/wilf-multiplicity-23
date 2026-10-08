# Wilf up to multiplicity 23: arXiv preprint and computational supplement

Public repository: https://github.com/JC8267/wilf-multiplicity-23

- [Paper PDF](manuscript.pdf) and [LaTeX source](manuscript.tex)
- [arXiv source archive](wilf_m23_arxiv_source.zip)
- [Submission metadata](ARXIV_SUBMISSION.md)

The manuscript is by Jason Collier, dated 5 October 2026. It discloses both
the computer-assisted proof and the AI assistance used during preparation.
Its proof uses the path certificate and the shape inequality
`W >= PC >= R0 - D`, with a direct certificate for the sole required exception
at `(d,m)=(3,21)`. It does not depend on the residue-charge lemma (139), the
H-branch, the proposed anticode conjecture, or an unrestricted `e=4` claim.

The paper is based on corrected Sections 87--92 of `WILF_GLOBAL_ATTACK.md`.
Original research files were not edited.

In the local package, `manuscript.tex` and `manuscript.pdf` are alongside this
file. In the arXiv source archive, the TeX source is at the archive root and
the computational supplement is in `anc/`; the compiled PDF is excluded.
Download and extract the complete arXiv source archive to preserve the
supplement's directory structure. Run the commands below from its directory.

## What is included

- `manuscript.tex`: self-contained analytical reduction, enumeration coverage
  arguments, the 14-row table, the explicit exceptional shape, and references.
- `manuscript.pdf`: the manuscript compiled with Tectonic 0.17.0 (8 pages, no
  TeX warnings).
- `verify.py`: standard-library checks of frozen evidence, the full-rerun
  outputs, the exceptional tile, genuine semigroup identities, and optional
  fresh small enumerations.
- `rerun_2026-10-05/`: complete outputs of the full reruns of both production
  programs, with commands, environments and run times (`RUNS.md`), plus the
  outputs of the two independent checks below.
- `shape_first_d3.py`: an independent recount of the `d=3` rows that shares no
  code with the production programs (needs `numpy`).
- `genus_sweep.py`: checks the analytical chain on every numerical semigroup up
  to a given genus (standard library only).
- `tiles_enum.py`: the existing exact-cover enumerator, with its absolute import
  removed and its only required helper inlined. No enumeration rule changed.
- `census.py`: the existing lean census, with portable paths and additional
  explicit `R0-D` statistics. It writes summary and exceptional-tile records to
  the chosen output directory. Its enumeration and old margin are unchanged.
- `independent.c`: an unchanged copy of the final independent C enumerator.
- `independent_original.c`: the earlier C version associated with the `orb_*.log`
  family, retained for provenance.
- `data/`: unmodified archived summaries and relevant completion logs.
- `manifest.json`: SHA-256 hashes and source mappings recorded during preparation.
- `verification_results.json`: results of the most recent local verifier run.
- `AUDIT.md`: proof review, enumeration review, checks performed, and open work.

## Run the bounded checks

From this directory, using Python 3.10 or newer:

```text
python verify.py --smoke
```

No third-party Python package is needed. The command checks hashes and all
99 saved extremal records, compares all 14 required weighted counts, calculates
the 96 certificates for the exception, tests 58 genuine semigroups, and compares
complete tile sets in 14 fresh small cases through multiplicity 9. It writes
`verification_results.json`. The small-case linear-extension implementation in
the verifier is separate from the exact-cover enumerator; it is not a replay
of the compiled production C binary. Both commands also check every saved
full-rerun output in `rerun_2026-10-05/` against the table and the exception.

Without `--smoke`, it skips the fresh small enumerations. Neither command reruns
the large production census for multiplicities 20--23. If run without `--smoke`,
the new results file will correctly contain an empty fresh-enumeration list.

To check the portable census entry point on a small case, use a fresh directory:

```text
python census.py 3 9 checks/summary.jsonl
```

This case has 52 representatives and 276 weighted tiles. Summary and witness
files are appended, so use a new output directory for a new experiment.

## Reproduce the full computation

Both algorithms were rerun in full on 5 October 2026; `rerun_2026-10-05/RUNS.md`
records the commands, environments and results. These reruns are the evidence
for the manuscript table. The archived terminal lines in `data/` agree with them
but are historical, and some came from source revisions not retained here.

For the independent algorithm, use GNU C (the source uses GNU statement
expressions). For example, on a host with GCC:

```text
gcc -O3 -std=gnu11 independent.c -o independent
./independent 3 20 23 > fresh_d3.log
./independent 4 20 23 > fresh_d4.log
./independent 5 20 23 > fresh_d5.log
./independent 6 22 23 > fresh_d6.log
```

On this Windows machine, GCC is available inside WSL (Ubuntu). Run the commands
above inside WSL. Each `(d,m)` row can run as a separate process.
`rerun_2026-10-05/c/run.sh` is the retained original runner and uses the
relative paths of the original scratch directory; use the commands above
when reproducing the calculation from this package.

For the Python census, run the following from this directory in PowerShell,
with a fresh `rerun` directory:

```powershell
foreach ($wilfM in 20..23) {
    foreach ($wilfD in 3..6) {
        if (3 * ($wilfD + 1) -lt $wilfM) {
            python census.py $wilfD $wilfM rerun/summary.jsonl
            if ($LASTEXITCODE -ne 0) { throw "Census failed: d=$wilfD m=$wilfM" }
        }
    }
}
```

Record interpreter/compiler versions, flags, commands, exit codes and file
hashes with each fresh run. Compare all 14 weighted counts to the manuscript
table and all `R0-D` minima to the independent outputs. Inspect every dumped
`RD_TILES.jsonl` record; the only required exceptional representative should
be `(3,21)`, equivalent to the shape in the manuscript. Its full label orbit
must be checked at every maximal target, as `verify.py` does for the archived
representative. Do not infer positivity of `R0-D` from the older `min_margin`
field: that field is `R0-min(H,D)`.

## Manuscript status

`manuscript.pdf` was compiled with Tectonic 0.17.0, which downloads the TeX
packages it needs on first use:

```powershell
tectonic manuscript.tex
```

The final source was rebuilt in place with the existing Tectonic executable.
The TeX log has no warnings, undefined references or over/underfull boxes.
Tectonic printed a Fontconfig configuration message; the PDF was produced
successfully and its pages were inspected. The built-in editor compiler still
fails with `Unable to find standard directories for platform`.

`ARXIV_SUBMISSION.md` in the local package contains upload metadata and the
archive description; it is excluded from the arXiv archive. The submission
license must be selected by the author during upload. No external referee
review has been obtained. The arXiv submission has not yet been completed.
