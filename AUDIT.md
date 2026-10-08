# Submission-preparation audit — 5 October 2026

## Analytical reconstruction

The manuscript gives a proof chain with no reference to equation numbers in
the attack notes:

1. Lexicographically selected Apéry factorizations form a downset. A smaller
   divisor factorization could be substituted into its containing factorization,
   contradicting lexicographic minimality. Units and distinct nonzero labels
   follow from minimality of the generators.
2. For every function on the downset,
   `sum(mu*f) = d*sum(f) + sum_b sum_j b_j*(f(b)-f(b-e_j))`.
   This gives `sum(mu)=dm` and the first-moment identities.
3. Write `beta=max(Apéry)`, `r=beta mod m`, `l=m-1-r`, and
   `ell_b=floor((beta-w_b)/m)`. Then `n=sum(ell_b)` and `c=mq-l`.
   Substitution in the endpoint identity gives `W=p_r+sum(mu*ell)`.
4. Positivity of each lift `h_j>=1` gives the longest-path bound
   `ell_b>=E_r(b)`, hence `W>=PC_r`.
5. A carry difference is exactly `1[a_j>rho_t(b)]`. The summation identity
   and residue bijectivity give `p_t=-sum(F_t)`. The manuscript proves
   `F_t(b)<=|b|-2` for degree at least two and `F_t(b)<=0` in degrees zero
   and one. Thus `p_t>=-D`.
6. Monotonicity of the carry level gives `R_t>=R0` and therefore
   `W>=PC_r>=R0-D`.

No gap was found in this reconstruction. A second, separate line-by-line check
on 5 October 2026 also found no gap, and `genus_sweep.py` tests every step on
all 258,582 numerical semigroups of genus at most 22. This is a local review,
not external refereeing or a formal proof-assistant certificate. The shape inequality is
sufficient; it is not asserted for all cyclic tiles. In particular, the
21-cell exception has `R0-D=-2`.

## Enumeration coverage review

The exact-cover pool contains every cell whose box has injective residues.
Every such cell has box volume at most `m`, so each coordinate is bounded.
The property is inherited by every divisor. The last parent to enter the
pool will eventually be processed, allowing the child to be considered after
all parents are present. Every cell of a valid tile is therefore generated.
Choosing a cell forces its entire box; consistency rejects precisely conflicts
with already assigned residues. Deterministic residue selection gives a unique
successful branch per tile. No cap or degree cutoff is used in the census.

The linear-extension program includes every possible cell using the degree
and box-plus-missing-units bounds proved in the paper. Every downset has a unique
increasing sequence in its fixed order. Parent membership and unused residues
are necessary conditions. An excluded earlier parent can never be reintroduced,
so the dead-residue prune is valid. The original and final C sources were
retained. An independent count of the candidate sets in all 14 required cases
found at most 723 cells, below both the final candidate capacity (65,536) and
the per-residue-list capacity (8,256). Dimension, residue and stack indices are
also within their static limits for these cases. The candidate and residue-list
capacities fail explicitly when exceeded.

Unit scaling is a residue bijection; label sorting is a coordinate permutation.
These operations preserve the shape statistics and give bijections between the
corresponding tile sets. Orbit weights count distinct sorted label vectors,
not necessarily all units. Path certificates are not assumed invariant under
unit scaling: the exception is checked under all twelve units explicitly.

The census originally used `R0-min(H,D)`. The draft theorem deliberately avoids
using that old margin as a proof of `R0>=D`. It uses the `R0-D` minima recorded
by both programs in the full reruns and the direct exceptional certificate.
Both reruns dump the single exceptional tile explicitly.

## Evidence checked in this preparation

- Recomputed the saved endpoint weights, height compensation, degree and support
  statistics for all 99 extremal records in the two frozen JSONL files.
- Compared weighted counts and old minimum margins on all 14 required rows.
  These rows comprise 19,877,474 representatives and 318,252,397 weighted tiles.
- Checked that the independent logs report no `R0<D` representative in those
  rows except one at `(d,m)=(3,21)`, with minimum `R0-D=-2` there.
- Recomputed all 96 unit/maximal-target certificates of that explicit exception.
  Their minimum is 15; the per-unit minima are in the paper and JSON results.
- Independently computed Apéry sets by Dijkstra, counted elements below the
  conductor, selected factorizations, and checked `W=p+sum(mu*ell)` and
  `W>=PC>=R0-D` on 8 retained fixtures and 50 seeded genuine semigroups.
- Freshly compared complete tile sets from exact-cover and a separate Python
  linear-extension implementation in 14 small `(d,m)` cases through `m=9`,
  without unit-orbit reduction. Counts agree with the archived primary census.
  Every target on each fresh tile was checked for the carry estimate and the
  certificate identities.
- Ran the portable census command on a small case, confirming its entry point,
  output handling, weighted count and explicit `R0-D` statistics.
- Reran both production programs in full on all 14 required rows from the
  retained sources (`rerun_2026-10-05/`): `independent.c` with GCC 13.3.0
  (`-O3 -std=gnu11`) under Ubuntu 24.04 in WSL, and `census.py` with CPython
  3.14.5 under Windows 11. Every weighted count, old minimum margin, minimum
  `R0-D` and exception count matches the archived outputs, and the Python
  representative counts match. Both runs dump exactly one `R0<D` tile, at
  `(d,m)=(3,21)`, identical to the shape in the manuscript. `verify.py` checks
  these outputs.
- Recounted the four `d=3` rows with `shape_first_d3.py`, which shares no code
  with either production program: it enumerates every downset of size `m` in
  `N^3` containing the units (as nested Young diagrams) and tests all
  increasing label vectors for bijectivity. All four columns match, including
  the exception and its 12 per-unit certificate minima.
- Checked Lemmas 2.1, 2.3, 4.1, 4.2, Proposition 3.1 and Theorem 3.2 with
  `genus_sweep.py` on every numerical semigroup of genus at most 22 (258,582,
  matching the known counts by genus), with the carry and height bounds tested
  at every target. Fourteen have `R0<D`; the path certificate covers each.
- Rebuilt the final `manuscript.tex` in place with Tectonic 0.17.0: 8 pages,
  no TeX warnings, undefined references or over/underfull boxes. Tectonic
  printed a Fontconfig configuration message but returned exit code zero.
  The built-in compiler still fails with an environmental standard-directory
  error. The final PDF pages were inspected visually.
- Repeated `verify.py --smoke` after checking the completed reruns. The
  verifier now also checks all 14 recorded C exit codes, counts the dumped C
  exceptions, checks the Python row identities and empty stderr files, and
  compares the four saved shape-first recounts and their certificates.
- Reran `genus_sweep.py 10`: all assertions passed on 478 semigroups. The
  retained full genus-22 run contains 258,582 semigroups; it was not repeated
  during this final preparation.

These checks passed. The extremal-record checks alone cannot establish
enumeration completeness; the full reruns and the shape-first recount address it.

## Provenance and unresolved release work

The manifest records hashes when these files were frozen, not hashes captured
when the historical calculations were originally executed. Existing source
revisions and logs cannot by themselves bind an old executable to a source
revision or recover compiler/interpreter versions. The earlier `orb_*.log`
family is associated with the earlier independent source. `p2u_d5.log` was
produced by an intermediate revision that is not retained: its output line
lacks the `U<H` fields printed by `independent.c`, and its `too many cells`
failure at `(d,m)=(5,21)` cannot occur with the retained source, whose
candidate sets have at most 723 cells. `data/summary.jsonl` was produced by a
census variant that also canonicalised shapes (its `shapes` fields are
nonzero); that variant is not retained either. The parser only accepts explicit
completed-row lines and does not treat the failed attempt as completion.

The 2026-10-05 reruns from the retained sources reproduce all of these archived
values and replace them as the evidence for the table. They record source
hashes, environments, commands and run times (`rerun_2026-10-05/RUNS.md`). The
C runs recorded exit code 0. The Python runs were started without capturing
exit codes; each wrote its summary record, which happens only after the
enumeration completes, and each left stderr empty.

Mathematical novelty of the path certificate should be reviewed against the
existing Apéry/monomial/divset literature. The numerical range extends the
published fixed-multiplicity bound of 19 in the sources checked (Marashdeh,
August 2026, still states `m<=19`), but this does not prove absence of
unpublished competing work.

Manuscript edits made after this review, on 5 October 2026: added the
Dobbs–Matthews citation for `e<=3` (Marashdeh attributes `e<=3` to both
Fröberg–Gottlieb–Häggkvist and Dobbs–Matthews); renamed `|b|` from `h` to `k`
in the carry-lemma proof, since `h` is the height vector; removed an
unnecessary first sentence from the path-bound proof; replaced the unproved
remark on a "relaxation with real shared heights" with the statement that the
bound uses only `h_j>=1` and `ell_z>=0`; and spelled out in the proof of
Lemma 2.1 why the units lie in `B`, why `|B|=m` and why `phi` is bijective.
The mathematical content is unchanged.

Jason Collier is the sole named author, as requested. The final manuscript
discloses AI assistance in mathematical exploration, proof development, code
preparation, drafting and review, separately from the exhaustive computations
that support the computer-assisted theorem. No affiliation was supplied.

The arXiv source archive places the manuscript at the root and code, data,
run records and verification instructions in `anc/`. Its ancillary manifest
hashes the included supplement files; the local manifest also hashes the
manuscript and locally compiled PDF. Author details and a proposed public
delivery format are therefore resolved. A submission license must still be
chosen by the author in the arXiv upload workflow. No external referee review
has been obtained. The arXiv submission has not yet been completed.

## Public repository preparation — 7 October 2026

The author authorized creation of a public GitHub repository containing this
paper and its reproducibility files. This copy preserves the production sources
and run evidence; only repository links and distribution-status documentation
were updated. The arXiv source archive is the verified 5 October package.
