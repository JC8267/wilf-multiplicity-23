/* Independent enumerator of cyclic labelled tiles (Section 91 audit).
   For each strictly increasing a in [1,m)^d with gcd(a_1..a_d, m) = 1, enumerate every downset B of N^d with
   |B| = m containing 0 and all units, with phi(b) = a.b mod m injective (hence bijective), by building B
   as an increasing sequence in a fixed linear extension (graded, then lexicographic) of the candidate cells.
   Each downset arises exactly once.  For each tile compute the margin R0 - min(H, D) from the definitions.
   Prints per (d,m): number of tiles, number with negative margin, minimum margin.
   usage: indep d mlo mhi */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAXC 16384
static int d, m, a[8], ncell, cell[MAXC][8], key[MAXC], par[MAXC][8], npar[MAXC], res[MAXC];
static int inB[MAXC], used[64], deg[MAXC], child[MAXC][8];
static int stack[64], top; static int lastidx[64];
static long long ntiles, nneg, nnegD; static int minmargin, minmarginD;
static int idx_of(int *c){ /* linear search via hash over small grid */
    for (int i = 0; i < ncell; i++){ int ok = 1; for (int j = 0; j < d; j++) if (cell[i][j] != c[j]){ ok = 0; break; } if (ok) return i; }
    return -1;
}
static int gcd(int x, int y){ while (y){ int t = x % y; x = y; y = t; } return x; }
static void margin_eval(void){
    /* B = stack[0..top-1] (cell indices). compute mu, height, R0, D, H */
    static int inb[MAXC]; static int ht[MAXC];
    for (int i = 0; i < top; i++) inb[stack[i]] = 1;
    /* heights: process in decreasing degree order: stack is increasing in linear extension, so reverse order works */
    long long R0 = 0, D = 0, H = 0;
    for (int k = top - 1; k >= 0; k--){
        int c = stack[k]; int h = 0;
        for (int j = 0; j < d; j++){
            int id = child[c][j];
            if (id >= 0 && inb[id]){ if (ht[id] + 1 > h) h = ht[id] + 1; }
        }
        ht[c] = h;
    }
    for (int k = 0; k < top; k++){
        int c = stack[k]; int mu = 0;
        for (int j = 0; j < d; j++){
            int id = child[c][j];
            if (id < 0 || !inb[id]) mu += cell[c][j] + 1;
        }
        R0 += (long long)mu * ht[c];
        if (deg[c] > 2) D += deg[c] - 2;
        int sp = 0; for (int t = 0; t < d; t++) if (cell[c][t]) sp++;
        if (sp > 1) H += sp - 1;
    }
    for (int i = 0; i < top; i++) inb[stack[i]] = 0;
    long long mg = R0 - (H < D ? H : D);
    ntiles++; if (mg < 0) nneg++; if (R0 - D < 0) nnegD++; if (R0 - D < minmarginD) minmarginD = (int)(R0 - D);
    if (mg < minmargin) minmargin = (int)mg;
}
static void rec(int last){
    if (top == m){ margin_eval(); return; }
    /* units must all be present: they are the first d+1 cells in the order (0 and units), forced below */
    for (int r = 0; r < m; r++) if (!used[r] && lastidx[r] <= last) return;   /* dead: residue r can no longer be covered */
    for (int c = last + 1; c < ncell; c++){
        if (used[res[c]]) continue;
        int ok = 1; for (int k = 0; k < npar[c]; k++) if (!inB[par[c][k]]){ ok = 0; break; }
        if (!ok) continue;
        /* remaining capacity check not needed for correctness */
        inB[c] = 1; used[res[c]] = 1; stack[top++] = c;
        rec(c);
        top--; inB[c] = 0; used[res[c]] = 0;
    }
}
static int cmpcell(const void *x, const void *y){
    const int *p = (const int *)x, *q = (const int *)y; int sp = 0, sq = 0;
    for (int j = 0; j < 8; j++){ sp += p[j]; sq += q[j]; }
    if (sp != sq) return sp - sq;
    for (int j = 0; j < 8; j++) if (p[j] != q[j]) return q[j] - p[j];
    return 0;
}
int main(int argc, char **argv){
    d = atoi(argv[1]); int mlo = atoi(argv[2]), mhi = atoi(argv[3]);
    for (m = mlo; m <= mhi; m++){
        /* candidate cells: all b with |b| <= m-d (a downset of size m containing units has max degree <= m-d) */
        int maxdeg = m - d; ncell = 0;
        int c[8] = {0};
        /* enumerate all vectors with sum <= maxdeg */
        static int tmp[MAXC * 4][8]; int nt = 0;
        int v[8]; memset(v, 0, sizeof v);
        while (1){
            int s = 0; for (int j = 0; j < d; j++) s += v[j];
            if (s <= maxdeg){ if (nt >= MAXC){ fprintf(stderr, "too many cells\n"); return 1; } memset(tmp[nt], 0, sizeof(int) * 8); memcpy(tmp[nt], v, sizeof(int) * d); nt++; }
            int j = 0; while (j < d){ v[j]++; int s2 = 0; for (int t = 0; t < d; t++) s2 += v[t]; if (s2 <= maxdeg) break; v[j] = 0; j++; }
            if (j == d) break;
        }
        qsort(tmp, nt, sizeof(tmp[0]), cmpcell);
        ncell = nt;
        for (int i = 0; i < ncell; i++){ memcpy(cell[i], tmp[i], sizeof(int) * 8); deg[i] = 0; for (int j = 0; j < d; j++) deg[i] += cell[i][j]; }
        { static int hk[1 << 20]; static int hv[1 << 20]; int HM = (1 << 20) - 1;
          for (int i = 0; i <= HM; i++) hv[i] = -1;
          #define HASHV(v) ({ unsigned long long hh = 1469598103934665603ULL; for (int t = 0; t < d; t++) { hh ^= (unsigned)(v)[t] + 1; hh *= 1099511628211ULL; } (int)(hh & HM); })
          for (int i = 0; i < ncell; i++){ int h = HASHV(cell[i]); while (hv[h] >= 0) h = (h + 1) & HM; hv[h] = i; }
          for (int i = 0; i < ncell; i++) for (int j = 0; j < d; j++){
              int nc[8]; memcpy(nc, cell[i], sizeof(int) * 8); nc[j]++; child[i][j] = -1;
              if (deg[i] + 1 > maxdeg) continue;
              int h = HASHV(nc);
              while (hv[h] >= 0){ int q = hv[h]; int ok = 1; for (int t = 0; t < d; t++) if (cell[q][t] != nc[t]){ ok = 0; break; } if (ok){ child[i][j] = q; break; } h = (h + 1) & HM; }
          }
          for (int i = 0; i < ncell; i++){ npar[i] = 0; }
          for (int i = 0; i < ncell; i++) for (int j = 0; j < d; j++) if (child[i][j] >= 0){ int q = child[i][j]; par[q][npar[q]++] = i; }
        }
        for (int i = 0; i < 0; i++){
            npar[i] = 0;
            for (int j = 0; j < d; j++) if (cell[i][j]){ int p[8]; memcpy(p, cell[i], sizeof(int) * d); p[j]--; par[i][npar[i]++] = idx_of(p); }
        }
        ntiles = 0; nneg = 0; nnegD = 0; minmargin = 1 << 30; minmarginD = 1 << 30;
        /* strictly increasing labels */
        int A[8]; for (int j = 0; j < d; j++) A[j] = j + 1;
        while (1){
            if (A[d - 1] < m){
                int g = m; for (int j = 0; j < d; j++) g = gcd(g, A[j]);
                int weight = 0, minimal = 1;
                if (g == 1){
                    /* unit-scaling orbit: collect distinct sorted images; skip unless A is lexicographically minimal */
                    static int orb[4096][8]; int no = 0;
                    for (int u = 1; u < m && minimal; u++){
                        if (gcd(u, m) != 1) continue;
                        int B2[8]; for (int j = 0; j < d; j++) B2[j] = (int)(((long long)u * A[j]) % m);
                        for (int x = 1; x < d; x++){ int v = B2[x], y = x - 1; while (y >= 0 && B2[y] > v){ B2[y + 1] = B2[y]; y--; } B2[y + 1] = v; }
                        int cmp = 0; for (int j = 0; j < d; j++){ if (B2[j] != A[j]){ cmp = B2[j] < A[j] ? -1 : 1; break; } }
                        if (cmp < 0){ minimal = 0; break; }
                        int dup = 0; for (int o = 0; o < no && !dup; o++){ int same = 1; for (int j = 0; j < d; j++) if (orb[o][j] != B2[j]){ same = 0; break; } if (same) dup = 1; }
                        if (!dup){ memcpy(orb[no], B2, sizeof(int) * d); no++; }
                    }
                    weight = no;
                }
                if (g == 1 && minimal){
                    long long before = ntiles;
                    memcpy(a, A, sizeof(int) * d);
                    for (int i = 0; i < ncell; i++){ long long s = 0; for (int j = 0; j < d; j++) s += (long long)a[j] * cell[i][j]; res[i] = (int)(s % m); }
                    for (int r = 0; r < m; r++) lastidx[r] = -1; for (int i = 0; i < ncell; i++) lastidx[res[i]] = i;
                    /* cells 0..d are origin and units (order: degree, then lex descending puts e_1 first) */
                    memset(inB, 0, sizeof(int) * ncell); memset(used, 0, sizeof used); top = 0;
                    int okk = 1;
                    for (int i = 0; i <= d; i++){ if (used[res[i]]){ okk = 0; break; } used[res[i]] = 1; inB[i] = 1; stack[top++] = i; }
                    if (okk) rec(d);
                    ntiles = before + (ntiles - before) * weight;
                }
            }
            int j = d - 1; while (j >= 0 && A[j] >= m - (d - 1 - j) - 1) j--;
            if (j < 0) break;
            A[j]++; for (int t = j + 1; t < d; t++) A[t] = A[t - 1] + 1;
        }
        printf("d=%d m=%d tiles=%lld negative_margin=%lld min_margin=%d  R0<D(needs 139)=%lld min(R0-D)=%d\n", d, m, ntiles, nneg, minmargin, nnegD, minmarginD);
        fflush(stdout);
    }
}
