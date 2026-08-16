/* sweep_main.c -- the pre-registered sweep, one compiled binary per migration pair.
 * Includes the frozen erd.c (commit 942e713) for the objective, router and repair; the pair's
 * data arrives through the erd_data.h symlink, the pair id through -DPAIR_ID. Routed style
 * only, per the pre-registration. CSV to stdout:
 *   meta,pair,nfixed,nnew,nedge,disp,centroid_S,human_S,cal_cross,cal_pen
 *   feas,pair,who,cross,pen              (who: centroid, human, or method at budget 8000)
 *   run,pair,method,budget,seed,best_S
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
    double lo[64], hi[64], xh[64], xc[64], pen;
    long i, k, m, s, bi, nnew, nv, nc;

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
            g.ofr0[i] = ((double)(seen[g.e[i][0]]++ + 1) / (double)(deg[g.e[i][0]] + 1)
                         - 0.5) * 0.8;
            g.ofr1[i] = ((double)(seen[g.e[i][1]]++ + 1) / (double)(deg[g.e[i][1]] + 1)
                         - 0.5) * 0.8;
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

    for (k = 0; k < nnew; k++) {
        xh[2*k] = erd_cx[g.nfixed + k];
        xh[2*k+1] = erd_cy[g.nfixed + k];
    }
    centroid_place(&g, xc);
    legal(xc, &g);

    layout_report(&g, xh, rt, &nc, &pen);
    printf("meta,%d,%d,%d,%d,%g,%.10g,%.10g,%ld,%.10g\n", PAIR_ID,
           ERD_NFIXED, ERD_NNEW, ERD_NEDGE, (double)ERD_DISPLACEMENT,
           score(xc, &g), score(xh, &g), nc, pen);
    printf("feas,%d,human,%ld,%.10g\n", PAIR_ID, nc, pen);
    layout_report(&g, xc, rt, &nc, &pen);
    printf("feas,%d,centroid,%ld,%.10g\n", PAIR_ID, nc, pen);

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
                if (cjitter_run(cjitter_methods[m], &p, &bb, &r) != 0) return 1;
                printf("run,%d,%s,%ld,%ld,%.10g\n", PAIR_ID,
                       cjitter_methods[m], budgets[bi], s, r.best);
                if (budgets[bi] == 8000) {
                    memcpy(x8[m][s], xv, sizeof xv);
                    best8[m][s] = r.best;
                }
            }

    /* the median seed's layout at 8000, routed, per method: the McNemar binary's input */
    for (m = 0; cjitter_methods[m]; m++) {
        long idx[5] = { 0, 1, 2, 3, 4 }, t;
        for (i = 0; i < 5; i++)
            for (k = (long)i + 1; k < 5; k++)
                if (best8[m][idx[k]] < best8[m][idx[i]]) {
                    t = idx[i]; idx[i] = idx[k]; idx[k] = t;
                }
        layout_report(&g, x8[m][idx[2]], rt, &nc, &pen);
        printf("feas,%d,%s,%ld,%.10g\n", PAIR_ID, cjitter_methods[m], nc, pen);
    }
    return 0;
}
