"""Check the frozen evidence and replay small enumerations with Python's stdlib.

python verify.py           # archived counts, witnesses, exception, genuine examples
python verify.py --smoke   # additionally compare two enumerators on small cases
This does not rerun the production census for multiplicities 20--23; it checks the
saved outputs of the 2026-10-05 full reruns in rerun_2026-10-05/ when present.
"""
import argparse
import hashlib
import heapq
import itertools
import json
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def up(b, j):
    return b[:j] + (b[j] + 1,) + b[j + 1:]


def tile_terms(B, a, m):
    B = set(map(tuple, B))
    d = len(a)
    assert len(B) == m
    assert all(tuple(int(i == j) for i in range(d)) in B for j in range(d))
    assert (0,) * d in B
    assert all(b[j] == 0 or b[:j] + (b[j] - 1,) + b[j + 1:] in B
               for b in B for j in range(d))
    A = {b: sum(x * y for x, y in zip(a, b)) for b in B}
    assert sorted(x % m for x in A.values()) == list(range(m))
    mu = {b: sum(b[j] + 1 for j in range(d) if up(b, j) not in B) for b in B}
    Z = {b for b in B if all(up(b, j) not in B for j in range(d))}
    above = {b: [z for z in Z if all(x >= y for x, y in zip(z, b))] for b in B}
    R0 = sum(mu[b] * (max(map(sum, above[b])) - sum(b)) for b in B)
    D = sum(max(sum(b) - 2, 0) for b in B)
    H = sum(max(sum(x > 0 for x in b) - 1, 0) for b in B)
    assert sum(mu.values()) == d * m
    assert all(sum(mu[b] * b[j] for b in B) == (d + 1) * sum(b[j] for b in B)
               for j in range(d))
    return B, A, mu, Z, above, R0, D, H


def certificate(terms, a, m, t):
    B, A, mu, Z, above, R0, D, H = terms
    d = len(a)
    l = m - 1 - t
    N = {b: (A[b] + l) // m for b in B}
    p = l + sum(mu[b] * N[b] for b in B) - (d + 1) * sum(N.values())
    F = {}
    for b in B:
        rho = (A[b] + l) % m
        s = sum(b[j] for j in range(d) if a[j] > rho)
        F[b] = N[b] - s - int(rho > t)
        assert F[b] <= max(sum(b) - 2, 0)
    assert p == -sum(F.values()) and p >= -D
    psi = {b: sum(b) + N[b] for b in B}
    E = {b: max(psi[z] for z in above[b]) - psi[b] for b in B}
    R = sum(mu[b] * E[b] for b in B)
    assert R >= R0
    return p, R, p + R, E


def linear_tiles(a, m):
    """Small-case reference: fixed linear extension; no exact-cover code used."""
    d = len(a)
    candidates = [b for b in itertools.product(range(m - d + 1), repeat=d)
                  if sum(b) <= m - d
                  and math.prod(x + 1 for x in b) + sum(x == 0 for x in b) <= m]
    candidates.sort(key=lambda b: (sum(b), b))
    parents = {b: {b[:j] + (b[j] - 1,) + b[j + 1:] for j in range(d) if b[j]}
               for b in candidates}
    labels = {b: sum(x * y for x, y in zip(a, b)) % m for b in candidates}
    B = {(0,) * d} | {tuple(int(i == j) for i in range(d)) for j in range(d)}
    used = {labels[b] for b in B}
    assert len(used) == d + 1

    def rec(start):
        if len(B) == m:
            yield frozenset(B)
            return
        for k in range(start, len(candidates)):
            b = candidates[k]
            if labels[b] in used or not parents[b] <= B:
                continue
            B.add(b)
            used.add(labels[b])
            yield from rec(k + 1)
            used.remove(labels[b])
            B.remove(b)

    yield from rec(d + 1)


def genuine_check(gens):
    gens = sorted(set(gens))
    m = gens[0]
    assert math.gcd(*gens) == 1
    w = [math.inf] * m
    w[0] = 0
    queue = [(0, 0)]
    while queue:
        value, r = heapq.heappop(queue)
        if value != w[r]:
            continue
        for g in gens[1:]:
            new = value + g
            if new < w[new % m]:
                w[new % m] = new
                heapq.heappush(queue, (new, new % m))
    minimal = [g for g in gens[1:]
               if not any(w[(g - h) % m] <= g - h for h in gens if h < g)]
    d = len(minimal)
    facts = {0: (0,) * d}
    for value in sorted(w)[1:]:
        facts[value] = min(up(facts[value - g], j)
                           for j, g in enumerate(minimal) if value - g in facts)
    a = tuple(g % m for g in minimal)
    h = tuple(g // m for g in minimal)
    terms = tile_terms(facts.values(), a, m)
    B, A, mu, Z, above, R0, D, H = terms
    beta = max(w)
    c = beta - m + 1
    depths = {b: (beta - sum(g * x for g, x in zip(minimal, b))) // m for b in B}
    n = sum(w[x % m] <= x for x in range(c))
    assert n == sum(depths.values())
    W = (d + 1) * n - c
    p, R, PC, E = certificate(terms, a, m, beta % m)
    assert W == p + sum(mu[b] * depths[b] for b in B)
    assert all(depths[b] >= E[b] for b in B)
    assert W >= PC >= R0 - D
    return W, PC


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if (ROOT / 'manifest.json').exists():
        manifest = json.loads((ROOT / 'manifest.json').read_text())
        for item in manifest['files']:
            assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], item['path']
        print('PASS: frozen source/data SHA-256 hashes')
    rows = {}
    for filename in ('summary.jsonl', 'summary_lean.jsonl'):
        for line in (ROOT / 'data' / filename).read_text().splitlines():
            row = json.loads(line)
            key = row['d'], row['m']
            assert key not in rows
            rows[key] = row
            if row['min_tile'] is not None:
                t = row['min_tile']
                *_, R0, D, H = tile_terms(t['B'], t['a'], row['m'])
                assert (R0, D, H) == (t['R0'], t['D'], t['H'])
                assert R0 - min(H, D) == row['min_margin'] == t['margin']
    pattern = re.compile(r'^d=(\d+) m=(\d+) tiles=(\d+) negative_margin=(\d+) min_margin=(-?\d+)\s+R0<D\(needs 139\)=(\d+) min\(R0-D\)=(-?\d+)')
    logs = {}
    for path in sorted((ROOT / 'data').glob('*.log')):
        for line in path.read_text().splitlines():
            match = pattern.match(line)
            if match:
                d, m, count, negative, margin, rd, minimum = map(int, match.groups())
                record = (count, negative, margin, rd, minimum)
                if (d, m) in logs:
                    assert logs[d, m] == record
                logs[d, m] = record
    required = [(d, m) for m in range(20, 24) for d in range(3, 7) if 3 * (d + 1) < m]
    table = []
    for d, m in required:
        row = rows[d, m]
        count, negative, margin, rd, minimum = logs[d, m]
        assert count == row['tiles_all'] and margin == row['min_margin']
        assert negative == row['residual_tiles'] == 0
        assert rd == int((d, m) == (3, 21))
        assert minimum >= 0 or (d, m, minimum) == (3, 21, -2)
        table.append(dict(d=d, e=d + 1, m=m, representatives=row['tiles_rep'],
                          weighted_tiles=count, min_R0_minus_D=minimum, exceptions=rd))
    print(f'PASS: {len(rows)} extremal records; {len(required)} required census/log count agreements')
    exc = rows[3, 21]['min_tile']
    B, a, m = exc['B'], exc['a'], 21
    assert exc['R0'] == 15 and exc['D'] == 17
    values = []
    for u in range(1, m):
        if math.gcd(u, m) != 1:
            continue
        au = tuple(u * x % m for x in a)
        terms = tile_terms(B, au, m)
        for z in sorted(terms[3]):
            t = terms[1][z] % m
            PC = certificate(terms, au, m, t)[2]
            assert PC >= 0
            values.append(dict(unit=u, target=t, PC=PC))
    exception = dict(m=m, a=a, B=B, R0=15, D=17, certificates=values,
                     pairs=len(values), min_PC=min(v['PC'] for v in values))
    print(f"PASS: m=21 exception, {exception['pairs']} unit/target pairs, min PC={exception['min_PC']}")
    rerun = ROOT / 'rerun_2026-10-05'
    fresh_full = []
    if rerun.exists():
        exc_cells = sorted(map(tuple, exc['B']))
        for d, m in required:
            done = (rerun / 'c' / f'd{d}_m{m}.done').read_text().strip()
            assert re.fullmatch(r'exit=0 secs=\d+', done), (d, m, done)
            record = None
            c_exceptions = 0
            for line in (rerun / 'c' / f'd{d}_m{m}.log').read_text().splitlines():
                match = pattern.match(line)
                if match:
                    assert record is None
                    record = tuple(map(int, match.groups()))
                elif line.startswith('RD '):
                    c_exceptions += 1
                    head, cells = line.split('|')
                    assert list(map(int, head.split()[1:])) == [m, d, *exc['a']]
                    assert sorted(tuple(map(int, c.split(','))) for c in cells.split()) == exc_cells
            assert record == (d, m) + logs[d, m], (d, m)
            assert c_exceptions == logs[d, m][3], (d, m)
            out = rerun / 'python' / f'd{d}_m{m}'
            row = json.loads((out / 'summary.jsonl').read_text())
            assert (row['d'], row['m']) == (d, m)
            assert (out / 'stderr.txt').read_bytes() == b'', (d, m)
            count, negative, margin, rd, minimum = logs[d, m]
            assert (row['tiles_rep'], row['tiles_all'], row['min_margin'], row['residual_tiles']) == (rows[d, m]['tiles_rep'], count, margin, 0)
            assert (row['min_R0_minus_D'], row['rd_representatives']) == (minimum, rd)
            dumped = [json.loads(line) for line in (out / 'RD_TILES.jsonl').read_text().splitlines()]
            assert len(dumped) == rd
            assert all(t['a'] == exc['a'] and sorted(map(tuple, t['B'])) == exc_cells for t in dumped)
            fresh_full.append(dict(d=d, m=m, representatives=row['tiles_rep'], weighted_tiles=count,
                                   min_R0_minus_D=minimum, exceptions=rd))
        print(f'PASS: fresh full C and Python reruns reproduce all {len(fresh_full)} required rows and the exception')
        for m in range(20, 24):
            shape = json.loads((rerun / 'independent_checks' / f'shape_first_d3_m{m}.json').read_text())
            row = next(row for row in fresh_full if (row['d'], row['m']) == (3, m))
            assert all(shape[k] == row[k] for k in ('d', 'm', 'representatives', 'weighted_tiles', 'min_R0_minus_D'))
            assert shape['rd_representatives'] == row['exceptions']
            certs = shape['rd_certificates']
            assert len(certs) == row['exceptions']
            for rec in certs:
                assert rec['a'] == exc['a'] and sorted(map(tuple, rec['B'])) == exc_cells
                assert (rec['R0'], rec['D'], rec['n_maximal']) == (15, 17, 8)
                assert rec['min_PC_per_unit'] == {str(u): min(v['PC'] for v in values if v['unit'] == u)
                                                for u in sorted({v['unit'] for v in values})}
        print('PASS: all four saved shape-first recounts and their exceptional certificates')
    fixtures = [(16,22,39,111,129), (16,22,23,79,81), (83,85,457,467,944),
                (44,45,62,64,138,139,174), (16,23,27,28), (8,21,30,35),
                (63,83,92,161), (9,10,12,13)]
    expected = [(126,39), (39,39), (1235,915), (409,247), (19,19), (30,16), (278,252), (2,2)]
    for gens, result in zip(fixtures, expected):
        assert genuine_check(gens) == result
    rng = random.Random(23)
    random_checks = 0
    while random_checks < 50:
        m = rng.randint(2, 25)
        gens = [m] + rng.sample(range(m + 1, 6 * m), rng.randint(2, 6))
        if math.gcd(*gens) == 1:
            genuine_check(gens)
            random_checks += 1
    print('PASS: exact Wilf/path identities on 8 fixtures and 50 seeded genuine semigroups')
    smoke = []
    if args.smoke:
        from tiles_enum import enum_tiles
        for d in (3, 4, 5):
            for m in range(max(d + 1, 5), 10):
                count = 0
                for a in itertools.combinations(range(1, m), d):
                    if math.gcd(m, *a) != 1:
                        continue
                    units = {tuple(int(i == j) for i in range(d)) for j in range(d)}
                    exact = {frozenset(B) for B in enum_tiles(a, m) if units <= B}
                    linear = set(linear_tiles(a, m))
                    assert exact == linear, (d, m, a)
                    count += len(exact)
                    for B in exact:
                        terms = tile_terms(B, a, m)
                        for t in range(m):
                            certificate(terms, a, m, t)
                assert count == rows[d, m]['tiles_all'], (d, m, count)
                smoke.append(dict(d=d, m=m, weighted_tiles=count))
                print(f'PASS: fresh exact-cover/linear-extension enumeration d={d}, m={m}, tiles={count}')
    scope = ('Archived outputs and the 2026-10-05 full reruns of both production programs checked.'
             if fresh_full else 'Archived production outputs checked; production census not rerun.')
    result = dict(scope=scope, table=table, exception=exception, extremal_records=len(rows),
                  fresh_full_reruns=fresh_full, genuine_checks=58, fresh_small_enumerations=smoke)
    (ROOT / 'verification_results.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Wrote verification_results.json')


if __name__ == '__main__':
    main()
