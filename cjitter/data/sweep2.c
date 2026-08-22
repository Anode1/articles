/* sweep2.c -- the sweep the corrected paper needs, with the three gaps of sweep_block.c
 * closed. NOT a replacement for the record: sweep_main.c and sweep_block.c stay frozen as
 * what produced results.csv and block_results{,_fixed}.csv.
 *
 * What is new here, and why:
 *   PANEL      the panel size, -DPANEL=N (default 5, which must reproduce the record).
 *              NOT called SEEDS: erd.c defines SEEDS itself, unconditionally, and this
 *              file includes erd.c first, so -DSEEDS=101 was silently overridden back
 *              to 5 and a run that looked like a 101-seed panel was a 5-seed one.
 *              Five seeds let the one-sided sign test reach 0.05 only on a clean sweep.
 *   NODE_GAP   overridable, -DNODE_GAP=0.0. The repair fix and the clearance change from 0
 *              to 12 landed in one commit, so the corrected sweep optimizes a different
 *              feasible set. This arm separates the bug fix from the constraint change.
 *   feas rows  emitted for the centroid and the human as well as the four methods. The
 *              pre-registered secondary on the (C, P) pair could not be computed on
 *              block_results_fixed.csv because those two rows were never written.
 *   clearance  the closest pair of tables printed beside every reported layout, the check
 *              whose absence let the repair defect outlive four reviews.
 *
 * Rows carry the gap so both arms live in one file. Lines opening with '#' are comments.
 *   #  free text
 *   meta,pair,gap,nfixed,nnew,nedge,disp,centroid_S,human_S,cal_cross,cal_pen
 *   run,pair,gap,method,block,budget,seed,best,mean_disp_to_human
 *   disp,pair,gap,who,block,mean_disp_to_human
 *   feas,pair,gap,who,block,cross,pen,min_clearance
 */
#define main erd_main
#include "example/erd/erd.c"
#undef main

#ifndef PAIR_ID
#define PAIR_ID 0
#endif
#ifndef PANEL
#define PANEL 5
#endif
#ifndef PRIMARY_ONLY
#define PRIMARY_ONLY 0
#endif

/* Mean Euclidean distance, over the added tables, between a layout and the human's accepted
 * coordinates. On the 'seen' context the human's answer is a feasible point of the problem,
 * so this is a metric whose target is the maintainer by definition, with none of the routed
 * objective's construct problem. On the 'prev' context it is not, and the number is reported
 * only to show how far the two contexts differ. */
static double disp_to_human(const double *v, const double *xh, long nv)
{
    double s = 0;
    long i;
    for (i = 0; i < nv; i += 2) {
        double dx = v[i] - xh[i], dy = v[i+1] - xh[i+1];
        s += sqrt(dx * dx + dy * dy);
    }
    return s / (double)(nv / 2);
}

int main(void)
{
    static Erd g;
    static Route rt[MAXE];
    static double xs[4][PANEL][64];
    static double bests[4][PANEL];
    static const long all_budgets[4] = { 500, 2000, 8000, 32000 };
    const long *budgets = PRIMARY_ONLY ? all_budgets + 2 : all_budgets;
    const long nbudget  = PRIMARY_ONLY ? 1 : 4;
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
    printf("meta,%d,%g,%d,%d,%d,%g,%.10g,%.10g,%ld,%.10g\n", PAIR_ID, (double)NODE_GAP,
           ERD_NFIXED, ERD_NNEW, ERD_NEDGE, (double)ERD_DISPLACEMENT,
           score(xc, &g), score(xh, &g), nc, pen);

    /* The two reference layouts, on the feasibility order the pre-registration declared.
     * The human is drawn, not repaired, so its clearance is the maintainer's own. */
    printf("feas,%d,%g,human,-1,%ld,%.10g,%.10g\n", PAIR_ID, (double)NODE_GAP,
           nc, pen, min_clearance(&g, xh));
    layout_report(&g, xc, rt, &nc, &pen);
    printf("feas,%d,%g,centroid,-1,%ld,%.10g,%.10g\n", PAIR_ID, (double)NODE_GAP,
           nc, pen, min_clearance(&g, xc));
    printf("disp,%d,%g,centroid,-1,%.10g\n", PAIR_ID, (double)NODE_GAP,
           disp_to_human(xc, xh, nv));

    for (arm = 0; arm < 2; arm++) {
        long blk = arm == 0 ? nv : 2;          /* whole vector, then one table */
        if (arm == 1 && nv == 2) continue;     /* identical by construction, do not re-run */
        for (m = 0; cjitter_methods[m]; m++)
            for (bi = 0; bi < nbudget; bi++)
                for (s = 0; s < PANEL; s++) {
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
                    printf("run,%d,%g,%s,%ld,%ld,%ld,%.10g,%.10g\n", PAIR_ID,
                           (double)NODE_GAP, cjitter_methods[m], blk, budgets[bi], s,
                           r.best, disp_to_human(xv, xh, nv));
                    if (budgets[bi] == 8000) {
                        memcpy(xs[m][s], xv, sizeof xv);
                        bests[m][s] = r.best;
                    }
                }
        for (m = 0; cjitter_methods[m]; m++) {
            long idx[PANEL], tt;
            for (i = 0; i < PANEL; i++) idx[i] = i;
            for (i = 0; i < PANEL; i++)
                for (k = i + 1; k < PANEL; k++)
                    if (bests[m][idx[k]] < bests[m][idx[i]]) {
                        tt = idx[i]; idx[i] = idx[k]; idx[k] = tt;
                    }
            layout_report(&g, xs[m][idx[PANEL/2]], rt, &nc, &pen);
            printf("feas,%d,%g,%s,%ld,%ld,%.10g,%.10g\n", PAIR_ID, (double)NODE_GAP,
                   cjitter_methods[m], blk, nc, pen,
                   min_clearance(&g, xs[m][idx[PANEL/2]]));
        }
    }
    return 0;
}
