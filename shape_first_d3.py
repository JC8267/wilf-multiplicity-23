"""Independent shape-first recount of the d=3 census rows (m = 20..23).

Shares no code with tiles_enum.py / independent.c / verify.py.
1. Enumerate every downset B of N^3 with |B| = m containing 0, e1, e2, e3, as a
   chain of nested Young diagrams (layers z = 0, 1, 2, ...): plane partitions.
2. For each B, test every strictly increasing label vector a in [1, m-1]^3 for
   bijectivity of b -> a.b mod m (numpy, vectorised over labels).
3. Recompute weighted tile count, representative count, min(R0-D) and the R0<D
   list from first principles, plus path certificates for any R0<D tile.
"""
import itertools, json, math, sys, time
import numpy as np


def subpartitions(bound, n):
    """Weakly decreasing tuples mu with mu_i <= bound_i and sum n (no trailing zeros)."""
    out = []

    def rec(i, rem, cap, acc):
        if rem == 0:
            out.append(tuple(acc)); return
        if i >= len(bound):
            return
        hi = min(cap, bound[i], rem)
        # remaining rows can hold at most hi_each * rows_left
        for v in range(hi, 0, -1):
            rows_left = len(bound) - i
            if v * rows_left < rem:
                break
            acc.append(v); rec(i + 1, rem - v, v, acc); acc.pop()
    rec(0, n, n, [])
    return out


def downsets3(m):
    """Yield list of layers (Young diagrams) with total m, nested, layer0 has >=2 rows and >=2 cols, >=2 layers."""
    big = tuple([m] * m)

    def rec(prev, rem, layers):
        if rem == 0:
            yield list(layers); return
        for n in range(rem, 0, -1):
            for mu in subpartitions(prev, n):
                layers.append(mu); yield from rec(mu, rem - n, layers); layers.pop()
    for n0 in range(1, m + 1):
        for lam in subpartitions(big, n0):
            if len(lam) < 2 or lam[0] < 2:
                continue  # need (1,0,0) and (0,1,0)
            if n0 == m:
                continue  # need (0,0,1)
            yield from rec(lam, m - n0, [lam])


def cells_of(layers):
    return [(i, j, k) for k, lam in enumerate(layers) for i, row in enumerate(lam) for j in range(row)]


def shape_stats(B):
    S = set(B)
    d = 3
    up = lambda b, j: b[:j] + (b[j] + 1,) + b[j + 1:]
    mu = {b: sum(b[j] + 1 for j in range(d) if up(b, j) not in S) for b in B}
    Z = [b for b in B if all(up(b, j) not in S for j in range(d))]
    eta = {b: max(sum(z) for z in Z if all(z[j] >= b[j] for j in range(d))) - sum(b) for b in B}
    R0 = sum(mu[b] * eta[b] for b in B)
    D = sum(max(sum(b) - 2, 0) for b in B)
    assert sum(mu.values()) == d * len(B)
    return R0, D, mu, Z


def pc(B, a, m, t, mu, Z):
    d = 3; l = m - 1 - t
    A = {b: sum(x * y for x, y in zip(a, b)) for b in B}
    N = {b: (A[b] + l) // m for b in B}
    psi = {b: sum(b) + N[b] for b in B}
    E = {b: max(psi[z] for z in Z if all(z[j] >= b[j] for j in range(d))) - psi[b] for b in B}
    p = l + sum(mu[b] * N[b] for b in B) - (d + 1) * sum(N.values())
    return p + sum(mu[b] * E[b] for b in B), p


def main(m):
    t0 = time.time()
    units = [u for u in range(1, m) if math.gcd(u, m) == 1]
    labels = list(itertools.combinations(range(1, m), 3))
    L = np.array(labels, dtype=np.int64).T  # 3 x K
    reps = set()
    for a in labels:
        orb = {tuple(sorted(u * x % m for x in a)) for u in units}
        if min(orb) == a and math.gcd(m, *a) == 1:
            reps.add(a)
    is_rep = np.array([a in reps for a in labels])
    target = np.arange(m)[:, None]
    nshapes = weighted = nrep = 0
    min_rd = None; rd_list = []
    for layers in downsets3(m):
        B = cells_of(layers)
        assert len(B) == m
        nshapes += 1
        C = np.array(B, dtype=np.int64)
        V = np.sort((C @ L) % m, axis=0)
        ok = np.all(V == target, axis=0)
        k = int(ok.sum())
        if not k:
            continue
        weighted += k
        kr = int((ok & is_rep).sum())
        nrep += kr
        if kr:
            R0, D, mu, Z = shape_stats(B)
            min_rd = R0 - D if min_rd is None else min(min_rd, R0 - D)
            if R0 < D:
                for idx in np.nonzero(ok & is_rep)[0]:
                    rd_list.append(dict(a=labels[idx], B=sorted(B), R0=R0, D=D, Z=sorted(Z), mu=mu))
    out = dict(d=3, m=m, shapes_with_units=nshapes, weighted_tiles=weighted, representatives=nrep,
               min_R0_minus_D=min_rd, rd_representatives=len(rd_list), secs=round(time.time() - t0, 1))
    certs = []
    for rec in rd_list:
        B, a, mu, Z = rec['B'], rec['a'], rec['mu'], rec['Z']
        per_unit = {}
        for u in units:
            au = tuple(u * x % m for x in a)
            vals = []
            for z in Z:
                t = sum(x * y for x, y in zip(au, z)) % m
                vals.append(pc(B, au, m, t, mu, Z)[0])
            per_unit[u] = min(vals)
        certs.append(dict(a=list(a), B=[list(b) for b in B], R0=rec['R0'], D=rec['D'],
                          n_maximal=len(Z), min_PC_per_unit=per_unit))
    out['rd_certificates'] = certs
    print(json.dumps(out), flush=True)


if __name__ == '__main__':
    for m in map(int, sys.argv[1:]):
        main(m)
