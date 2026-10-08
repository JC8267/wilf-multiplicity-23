# Full reruns, 5 October 2026

Both production programs were rerun on all 14 required rows from the sources in
this package, on one machine, one process per row, all rows concurrently.

| Program | Environment | Command |
|---|---|---|
| `independent.c` | GCC 13.3.0, Ubuntu 24.04.3 LTS in WSL 2, kernel 6.6.87.2-microsoft-standard-WSL2 | `gcc -O3 -std=gnu11 independent.c -o indep`; `./indep d m m` (see `c/run.sh`, `c/env.txt`) |
| `census.py` | CPython 3.14.5, Windows 11 | `python census.py d m <dir>/summary.jsonl` (see `python/env.txt`) |

Machine: 13th Gen Intel Core i7-13800H, 20 logical processors, 32 GB RAM.
Source hashes: `independent.c` 9bc7fe8064fda510c6a14a5df677f1eaca4e5696cc53ec5e2ab482ea646d3785; `census.py` 19b76024568234f6c1abcf715eda7b3ab1d4f2b6b68b6e6b664c427a8c0e114d;
`tiles_enum.py` ca8db9f998c21f6ab7b509511316297e6f8b92f312766f026461f7bada5a16b2.

## Results

C = `independent.c`, Py = `census.py`. Times are wall-clock seconds while other rows ran concurrently.

| m | d | Representatives (Py) | Weighted (C) | Weighted (Py) | min(R0-D) C | min(R0-D) Py | Exceptions C | Exceptions Py | C exit | C s | Py s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 20 | 3 | 1,391 | 10,244 | 10,244 | 4 | 4 | 0 | 0 | 0 | 1 | 0.9 |
| 20 | 4 | 25,619 | 187,000 | 187,000 | 12 | 12 | 0 | 0 | 0 | 4 | 24.5 |
| 20 | 5 | 328,112 | 2,492,114 | 2,492,114 | 14 | 14 | 0 | 0 | 0 | 55 | 827.9 |
| 21 | 3 | 1,383 | 15,846 | 15,846 | -2 | -2 | 1 | 1 | 0 | 1 | 1.1 |
| 21 | 4 | 30,133 | 331,341 | 331,341 | 16 | 16 | 0 | 0 | 0 | 5 | 29.9 |
| 21 | 5 | 444,166 | 5,195,104 | 5,195,104 | 11 | 11 | 0 | 0 | 0 | 100 | 1026.0 |
| 22 | 3 | 1,763 | 17,265 | 17,265 | 0 | 0 | 0 | 0 | 0 | 1 | 1.4 |
| 22 | 4 | 41,611 | 397,790 | 397,790 | 14 | 14 | 0 | 0 | 0 | 10 | 45.4 |
| 22 | 5 | 664,133 | 6,574,135 | 6,574,135 | 12 | 12 | 0 | 0 | 0 | 221 | 1247.6 |
| 22 | 6 | 8,169,530 | 81,030,042 | 81,030,042 | 19 | 19 | 0 | 0 | 0 | 2622 | 5082.1 |
| 23 | 3 | 1,487 | 32,714 | 32,714 | 1 | 1 | 0 | 0 | 0 | 1 | 1.2 |
| 23 | 4 | 37,699 | 795,993 | 795,993 | 16 | 16 | 0 | 0 | 0 | 12 | 40.4 |
| 23 | 5 | 670,311 | 14,746,842 | 14,746,842 | 18 | 18 | 0 | 0 | 0 | 300 | 1261.0 |
| 23 | 6 | 9,460,136 | 206,425,967 | 206,425,967 | 16 | 16 | 0 | 0 | 0 | 4107 | 5301.3 |
| Total | | 19,877,474 | 318,252,397 | 318,252,397 | | | 1 | 1 | | | |

Every value equals the archived outputs in `data/` and the manuscript table; `verify.py` checks this.
Both programs dump exactly one `R0<D` tile, at `(d,m)=(3,21)` with `a=(1,4,5)`: see `c/d3_m21.log`
(`RD` line) and `python/d3_m21/RD_TILES.jsonl`. Its shape is the one in the manuscript.

The two Python `d=6` rows ran for about 81 minutes under Windows power throttling (about 65% of one
core each) before throttling was disabled for those two processes, so their times are not comparable
with the other rows. Scheduling does not affect the results.

## Independent checks

These share no code with the production programs and ran with CPython 3.14.5 (numpy 2.4.6) on Windows 11.

`shape_first_d3.py` enumerates every downset of size m in N^3 that contains the units and tests every
strictly increasing label vector for bijectivity (`independent_checks/shape_first_d3_m*.json`):

| m | Downsets | Weighted | Representatives | min(R0-D) | Exceptions | s |
|---|---|---|---|---|---|---|
| 20 | 73,400 | 10,244 | 1,391 | 4 | 0 | 228.9 |
| 21 | 116,421 | 15,846 | 1,383 | -2 | 1 | 519.7 |
| 22 | 183,472 | 17,265 | 1,763 | 0 | 0 | 1043.9 |
| 23 | 287,021 | 32,714 | 1,487 | 1 | 0 | 1433.7 |

For m=21 it also recomputes the 12 per-unit minima of the path certificate over the 8 maximal targets:
15, 22, 31, 23, 29, 23, 23, 22, 25, 22, 23, 23 (units 1, 2, 4, 5, 8, 10, 11, 13, 16, 17, 19, 20).

`genus_sweep.py 22` checks Lemmas 2.1, 2.3, 4.1, 4.2, Proposition 3.1 and Theorem 3.2 on every numerical
semigroup of genus at most 22 (`independent_checks/genus_sweep_g22.log`): 258,582 semigroups, matching the
known counts by genus; all assertions pass; 14 have `R0<D` and are covered by the path certificate.
