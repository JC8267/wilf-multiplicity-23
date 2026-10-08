"""Exact enumeration of ALL cyclic downset tiles for a given (m, a) (generator EX).
Candidate pool: cells c whose box [0,c] has injective labels (necessary). DFS over residues (fewest candidates first);
choosing c for its residue forces box(c); candidates conflicting with a forced assignment are pruned."""
import itertools


def up(b, j):
    return b[:j] + (b[j] + 1,) + b[j + 1:]

def pool(a, m, K=None):
    d = len(a); out = []
    # BFS over cells with injective boxes (box injectivity is inherited downward)
    start = tuple([0] * d); seen = {start}; stack = [start]
    while stack:
        c = stack.pop(); out.append(c)
        for j in range(d):
            x = up(c, j)
            if x in seen: continue
            vol = 1
            for v in x: vol *= v + 1
            if vol > m or (K is not None and sum(x) > K): continue
            # all lower neighbours must be in pool (box-injective) -> check directly
            if any(x[i] > 0 and (x[:i] + (x[i] - 1,) + x[i + 1:]) not in seen for i in range(d)): continue
            labs = set()
            ok = True
            for y in itertools.product(*[range(v + 1) for v in x]):
                r = sum(p * q for p, q in zip(a, y)) % m
                if r in labs: ok = False; break
                labs.add(r)
            if ok: seen.add(x); stack.append(x)
    # seen may include cells added before all lower neighbours were known; recheck
    P = [c for c in seen if all(c[i] == 0 or (c[:i] + (c[i] - 1,) + c[i + 1:]) in seen for i in range(d))]
    return P

def enum_tiles(a, m, cap=None, K=None):
    """K: optional max degree |c| <= K (enumerates exactly the tiles of degree <= K)."""
    d = len(a)
    P = pool(a, m, K)
    lab = {c: sum(p * q for p, q in zip(a, c)) % m for c in P}
    box = {c: [y for y in itertools.product(*[range(v + 1) for v in c])] for c in P}
    cand = [[] for _ in range(m)]
    for c in P: cand[lab[c]].append(c)
    assign = [None] * m
    res = []
    def consistent(c):
        for y in box[c]:
            z = assign[lab[y]]
            if z is not None and z != y: return False
        return True
    def rec():
        if cap and len(res) >= cap: return
        best = None
        for r in range(m):
            if assign[r] is None:
                cs = [c for c in cand[r] if consistent(c)]
                if not cs: return
                if best is None or len(cs) < len(best[1]): best = (r, cs)
                if len(cs) == 1: break
        if best is None:
            res.append(set(assign)); return
        r, cs = best
        for c in cs:
            newly = []
            for y in box[c]:
                if assign[lab[y]] is None: assign[lab[y]] = y; newly.append(lab[y])
            rec()
            for s in newly: assign[s] = None
    rec()
    return res
