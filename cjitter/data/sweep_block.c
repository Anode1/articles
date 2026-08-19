/* sweep_block.c -- the pre-registered sweep, re-run with cjitter_tuning.block.
 * NOT the frozen sweep_main.c: this one is on the current API and adds the block arm.
 * Arm "n" is block = the whole vector, which must reproduce results.csv byte for byte;
 * arm "2" is one table per proposal. CSV to stdout:
 *   run,pair,method,block,budget,seed,best_S
 *   feas,pair,method,block,cross,pen        (median seed's layout at budget 8000)
 */
#define main erd_main
#include "example/erd/erd.c"
#undef main

#ifndef PAIR_ID
#define PAIR_ID 0
#endif

int main(void)
{
    static Erd g;
    static Route rt[MAXE];
    static double x8[4][5][64];
    double best8[4][5];
    static const long budgets[4] = { 500, 2000, 8000, 32000 };
    cjitter_problem p;
    cjitter_budget b;
    cjitter_tuning t;
    double lo[64], hi[64], xh[64], xc[64], pen;
    long i, k, m, s, bi, nnew, nv, nc, arm;

    g.cw = ERD_CW; g.ch = ERD_CH;
    g.nfixed = ERD_NFIXED;
    nnew = ERD_NNEW;
    g.n = g.nfixed + nnew;
    for (i = 0; i < g.n; i++) {
        g.x[i] = erd_cx[i]; g.y[i] = erd_cy[i];
        g.w[i] = erd_w[i];  g.h[i] = erd_h[i];
    }
    g.ne = ERD_NEDGE;
    for (i = 0; i < g.ne; i++) { g.e[i][0] = erd_edge[i][0]; g.e[i][1] = erd_edge[i][1]; }
    {
        long deg[MAXN] = { 0 }, seen[MAXN] = { 0 };
        for (i = 0; i < g.ne; i++) { deg[g.e[i][0]]++; deg[g.e[i][1]]++; }
        for (i = 0; i < g.ne; i++) {
            g.ofr0[i] = ((double)(seen[g.e[i][0]]++ + 1) / (double)(deg[g.e[i][0]] + 1) - 0.5) * 0.8;
            g.ofr1[i] = ((double)(seen[g.e[i][1]]++ + 1) / (double)(deg[g.e[i][1]] + 1) - 0.5) * 0.8;
        }
    }
    g.straight = 0;
    g.konst = frozen_part(&g);

    nv = 2 * nnew;
    for (i = 0; i < nv; i += 2) {
        lo[i] = 0; hi[i] = g.cw;
        lo[i+1] = 0; hi[i+1] = g.ch;
    }
    p.n = nv; p.lo = lo; p.hi = hi; p.fitness = score; p.repair = legal; p.ctx = &g;
    b.evals = 8000; b.seed = 1; b.jitter = JITTER; b.pop = POP;

    for (k = 0; k < nnew; k++) { xh[2*k] = erd_cx[g.nfixed+k]; xh[2*k+1] = erd_cy[g.nfixed+k]; }
    centroid_place(&g, xc);
    legal(xc, &g);
    layout_report(&g, xh, rt, &nc, &pen);
    printf("meta,%d,%d,%d,%d,%g,%.10g,%.10g,%ld,%.10g\n", PAIR_ID,
           ERD_NFIXED, ERD_NNEW, ERD_NEDGE, (double)ERD_DISPLACEMENT,
           score(xc, &g), score(xh, &g), nc, pen);

    for (arm = 0; arm < 2; arm++) {
        long blk = arm == 0 ? nv : 2;          /* whole vector, then one table */
        for (m = 0; cjitter_methods[m]; m++)
            for (bi = 0; bi < 4; bi++)
                for (s = 0; s < 5; s++) {
                    cjitter_budget bb = b;
                    cjitter_result r;
                    double xv[64];
                    memset(&r, 0, sizeof r);
                    r.x = xv;
                    bb.evals = budgets[bi];
                    bb.seed = 1u + 7919u * (uint32_t)s;
                    t = cjitter_tuning_default(nv);
                    t.block = blk;
                    if (cjitter_run_tuned(cjitter_methods[m], &p, &bb, &t, &r) != 0) return 1;
                    printf("run,%d,%s,%ld,%ld,%ld,%.10g\n", PAIR_ID,
                           cjitter_methods[m], blk, budgets[bi], s, r.best);
                    if (budgets[bi] == 8000) { memcpy(x8[m][s], xv, sizeof xv); best8[m][s] = r.best; }
                }
        for (m = 0; cjitter_methods[m]; m++) {
            long idx[5] = { 0, 1, 2, 3, 4 }, tt;
            for (i = 0; i < 5; i++)
                for (k = (long)i + 1; k < 5; k++)
                    if (best8[m][idx[k]] < best8[m][idx[i]]) { tt = idx[i]; idx[i] = idx[k]; idx[k] = tt; }
            layout_report(&g, x8[m][idx[2]], rt, &nc, &pen);
            printf("feas,%d,%s,%ld,%ld,%.10g\n", PAIR_ID, cjitter_methods[m], blk, nc, pen);
        }
    }
    return 0;
}
