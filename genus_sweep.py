"""Check the manuscript's analytic chain on EVERY numerical semigroup of genus <= G.

For each S (generated via the standard semigroup tree), independently of verify.py:
  Lemma 2.1   B (lex-least Apery factorizations) is a downset of size m with origin+units, phi bijective
  Lemma 2.3   sum mu = dm, sum mu b_j = (d+1) sum b_j
  Prop 3.1    W = p_r + sum mu*ell     (W = e*n - c computed directly from S)
  Thm 3.2     ell_b >= E_r(b), W >= PC_r
  Lemma 4.1   p_t >= -D(B) for EVERY target t (not only r)
  Lemma 4.2   R_t >= R0(B) for every t
  Cor 4.3     W >= PC_r >= R0 - D
"""
import sys, time


def children(gaps, c, m):
    """Children in the tree: remove a minimal generator x >= c (x > Frobenius)."""
    inS = lambda x: x >= c or (x > 0 and x not in gaps) or x == 0
    out = []
    for x in range(max(c, 1), c + m + 1):
        # x minimal generator iff not a sum of two nonzero elements of S
        if not any(inS(y) and inS(x - y) for y in range(1, x // 2 + 1)):
            out.append(x)
    return out


def analyse(gaps, c):
    inS = lambda x: x >= c or x not in gaps
    m = next(x for x in range(1, c + 2) if inS(x))
    if m == 1:
        return None
    # minimal generators other than m: all minimal generators are < c + m
    S_small = [x for x in range(1, c + m) if inS(x)]
    gens = [x for x in S_small if not any(inS(y) and inS(x - y) for y in range(1, x // 2 + 1))]
    assert gens[0] == m
    g = gens[1:]
    d = len(g)
    # Apery set by direct definition
    ap = {}
    for x in range(0, c + m):
        if inS(x) and not inS(x - m) if x >= m else inS(x):
            ap[x % m] = x
    assert len(ap) == m
    # lex-least factorization over g (exponent vectors), by increasing value
    fact = {0: (0,) * d}
    for v in sorted(ap.values())[1:]:
        best = None
        for j, gj in enumerate(g):
            if v - gj in fact:
                cand = list(fact[v - gj]); cand[j] += 1; cand = tuple(cand)
                if best is None or cand < best:
                    best = cand
        assert best is not None
        fact[v] = best
    B = list(fact.values())
    Bs = set(B)
    w = {b: v for v, b in fact.items()}
    units = [tuple(int(i == j) for i in range(d)) for j in range(d)]
    assert len(Bs) == m and all(u in Bs for u in units)
    for b in B:
        for j in range(d):
            if b[j]:
                assert b[:j] + (b[j] - 1,) + b[j + 1:] in Bs
    a = [x % m for x in g]; h = [x // m for x in g]
    assert all(x >= 1 for x in h)
    A = {b: sum(x * y for x, y in zip(a, b)) for b in B}
    assert len({A[b] % m for b in B}) == m
    up = lambda b, j: b[:j] + (b[j] + 1,) + b[j + 1:]
    mu = {b: sum(b[j] + 1 for j in range(d) if up(b, j) not in Bs) for b in B}
    assert sum(mu.values()) == d * m
    for j in range(d):
        assert sum(mu[b] * b[j] for b in B) == (d + 1) * sum(b[j] for b in B)
    Z = [b for b in B if all(up(b, j) not in Bs for j in range(d))]
    above = {b: [z for z in Z if all(zz >= bb for zz, bb in zip(z, b))] for b in B}
    eta = {b: max(sum(z) for z in above[b]) - sum(b) for b in B}
    R0 = sum(mu[b] * eta[b] for b in B)
    D = sum(max(sum(b) - 2, 0) for b in B)
    # Wilf number directly
    n = sum(1 for x in range(c) if inS(x))
    W = (d + 1) * n - c
    beta = max(ap.values()); assert beta == c + m - 1
    r = beta % m
    ell = {b: (beta - w[b]) // m for b in B}
    assert sum(ell.values()) == n
    res = {}
    for t in range(m):
        l = m - 1 - t
        N = {b: (A[b] + l) // m for b in B}
        p = l + sum(mu[b] * N[b] for b in B) - (d + 1) * sum(N.values())
        psi = {b: sum(b) + N[b] for b in B}
        E = {b: max(psi[z] for z in above[b]) - psi[b] for b in B}
        R = sum(mu[b] * E[b] for b in B)
        assert p >= -D, ('carry', gaps, t)
        assert R >= R0, ('height', gaps, t)
        res[t] = (p, R, E)
    p, R, E = res[r]
    assert W == p + sum(mu[b] * ell[b] for b in B), ('identity', sorted(gaps))
    assert all(ell[b] >= E[b] for b in B), ('path', sorted(gaps))
    assert W >= p + R >= R0 - D, ('chain', sorted(gaps))
    return m, d, W, p + R, R0 - D


def main(G):
    t0 = time.time()
    level = [(frozenset(), 0, 1)]  # (gaps, conductor, multiplicity) ; N itself
    total = 0; slack0 = 0; rd_neg = 0; maxm = 0
    for genus in range(0, G + 1):
        nxt = []
        for gaps, c, m in level:
            out = analyse(gaps, c)
            total += 1
            if out:
                mm, d, W, PC, RD = out
                maxm = max(maxm, mm)
                slack0 += (W == PC)
                rd_neg += (RD < 0)
            if genus < G:
                for x in children(gaps, c, m):
                    ng = gaps | {x}
                    nm = m if x != m else x + 1
                    nxt.append((ng, x + 1, nm))
        print(f'genus {genus}: {len(level)} semigroups', flush=True)
        level = nxt
    print(f'TOTAL {total} semigroups genus<={G}: all assertions passed; '
          f'W==PC_r in {slack0}; R0<D (handled by path cert) in {rd_neg}; max m {maxm}; {time.time()-t0:.0f}s')


if __name__ == '__main__':
    main(int(sys.argv[1]))
