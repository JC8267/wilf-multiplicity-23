"""front_P2: exhaustive residual-labelability census.
For (d, m): enumerate all sorted label vectors a (distinct entries, gcd(a, m) = 1), reduced modulo the unit-scaling
symmetry a -> u*a mod m (u in Z_m^*), taking the lexicographically-min sorted vector of each orbit as representative.
For each representative, ALL cyclic downset tiles (front_N exact-cover enumerator), filtered to nondegenerate.
Tile counts are weighted by orbit size (#distinct sorted vectors in the orbit) = exact count over all sorted a.
Per tile: R0, D, H (label free), margin = R0 - min(H, D).  Residual = margin < 0.
usage: python census.py d m out_summary.jsonl  (residual tiles appended to RESIDUAL_TILES.jsonl)"""
import sys, time, json, itertools, os
from pathlib import Path
from math import gcd
from collections import Counter
from tiles_enum import enum_tiles

OUT_DIR = ''  # Set from the output filename in the command-line entry point.

def up(b, j): return b[:j] + (b[j] + 1,) + b[j + 1:]

def terms(B, d):
    S = B
    order = sorted(S, key=lambda b: -sum(b))
    Hh = {}; R0 = 0; D = 0; H = 0
    for b in order:
        s = sum(b); h = s; mu = 0
        for j in range(d):
            u = up(b, j)
            if u in S:
                if Hh[u] > h: h = Hh[u]
            else:
                mu += b[j] + 1
        Hh[b] = h
        R0 += mu * (h - s)
        if s > 2: D += s - 2
        k = sum(1 for x in b if x)
        if k > 1: H += k - 1
    return R0, D, H

def canon_shape(B, d):
    """canonical form of B under coordinate permutations: sort coords by an invariant, brute force within ties."""
    cols = []
    for j in range(d):
        cols.append(tuple(sorted(Counter(b[j] for b in B).items())))
    # finer invariant: multiset of (b_j, |b|, |supp b|)
    inv = [(cols[j], tuple(sorted(Counter((b[j], sum(b), sum(1 for x in b if x)) for b in B).items()))) for j in range(d)]
    idx = sorted(range(d), key=lambda j: inv[j])
    groups = [list(g) for _, g in itertools.groupby(idx, key=lambda j: inv[j])]
    best = None
    for perms in itertools.product(*[itertools.permutations(g) for g in groups]):
        perm = [j for p in perms for j in p]
        key = tuple(sorted(tuple(b[j] for j in perm) for b in B))
        if best is None or key < best: best = key
    return best

def orbit_reps(d, m):
    units = [u for u in range(1, m) if gcd(u, m) == 1]
    reps = []
    for a in itertools.combinations(range(1, m), d):
        g = m
        for x in a: g = gcd(g, x)
        if g != 1: continue
        orb = {tuple(sorted((u * x) % m for x in a)) for u in units}
        if min(orb) == a: reps.append((a, len(orb)))
    return reps

if __name__ == "__main__":
    d, m, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    OUT_DIR = str(Path(out).resolve().parent) + os.sep
    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    reps = orbit_reps(d, m)
    units = [e for e in [tuple(int(i == j) for i in range(d)) for j in range(d)]]
    ntiles_w = 0; ntiles_rep = 0; nres_w = 0
    min_rd = None; rd_reps = 0
    shapes = {}  # canonical shape -> (margin, R0, H, D, example a)
    exact_seen = {}
    margin_hist = Counter()  # weighted by orbit size
    minrec = None
    resf = open(OUT_DIR + 'RESIDUAL_TILES_raw.jsonl', 'a'); rdf = open(OUT_DIR + 'RD_TILES.jsonl', 'a')
    for a, w in reps:
        for B in enum_tiles(a, m):
            if not all(e in B for e in units): continue
            ntiles_rep += 1; ntiles_w += w
            R0, D, H = terms(B, d)
            min_rd = R0 - D if min_rd is None else min(min_rd, R0 - D)
            if R0 < D:
                rd_reps += 1
                rdf.write(json.dumps(dict(d=d, m=m, a=list(a), w=w, B=sorted(map(list, B)), R0=R0, H=H, D=D)) + '\n'); rdf.flush()
            mg = R0 - min(H, D)
            margin_hist[mg] += w
            if mg < 0:
                nres_w += w
                resf.write(json.dumps(dict(d=d, m=m, a=list(a), B=sorted(map(list, B)), R0=R0, H=H, D=D)) + '\n'); resf.flush()
            if minrec is None or mg < minrec['margin']:
                minrec = dict(margin=mg, R0=R0, H=H, D=D, a=list(a), B=sorted(map(list, B)))
    # distinct shapes up to coordinate permutation
    low_shapes = []
    hist = sorted(margin_hist.items())[:12]
    rec = dict(d=d, m=m, n_a_orbits=len(reps), n_a_total=sum(w for _, w in reps), tiles_rep=ntiles_rep,
               tiles_all=ntiles_w, shapes=len(shapes), residual_tiles=nres_w, min_margin=minrec and minrec['margin'],
               min_R0_minus_D=min_rd, rd_representatives=rd_reps,
               min_tile=minrec, margin_hist_low=hist, n_le5=sum(c for k, c in margin_hist.items() if k <= 5),
               shape_margin_hist_low=[],
               low_shapes=low_shapes[:12], secs=round(time.time() - t0, 1))
    with open(out, 'a') as f: f.write(json.dumps(rec) + '\n')
    print("d=%d m=%d orbits=%d tiles(all a)=%d [rep %d] shapes=%d residual=%d minmargin=%s n<=5=%d %.1fs" % (
        d, m, len(reps), ntiles_w, ntiles_rep, len(shapes), nres_w, rec['min_margin'], rec['n_le5'], rec['secs']), flush=True)
