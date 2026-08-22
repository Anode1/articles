/* layout_dump.c -- print the coordinates of the layouts the paper's figures show:
 * the maintainer's, the centroid heuristic's, and each method's best-of-panel result.
 * One line per layout: "name x0 y0 x1 y1 ..." for the added tables only.
 *   cc -DPAIR_ID=n -DPANEL=101 layout_dump.c c/cjitter.c c/rng.c -lm
 */
#define main erd_main
#include "example/erd/erd.c"
#undef main
#ifndef PAIR_ID
#define PAIR_ID 0
#endif
#ifndef PANEL
#define PANEL 101
#endif
#ifndef BUDGET
#define BUDGET 8000
#endif

/* Print the routes the objective actually reads, so the picture can be checked against the
 * number. The renderer re-derives routes independently; if the two disagree, the figure is
 * not showing what was scored. */
static void dump_routes(const char *tag, const double *v, Erd *g)
{
    static Route rt[MAXE];
    long a, nc; double pen; int s;
    layout_report(g, v, rt, &nc, &pen);
    for (a = 0; a < g->ne; a++) {
        printf("route %s %ld %d", tag, a, g->enew[a]);
        for (s = 0; s < rt[a].np; s++) printf(" %.6g %.6g", rt[a].px[s], rt[a].py[s]);
        printf("\n");
    }
}

static void dump(const char *tag, const double *v, long nv, Erd *g)
{
    long i, nc; double pen;
    static Route rt[MAXE];
    layout_report(g, v, rt, &nc, &pen);
    printf("%s %.10g %ld %.10g", tag, score((double *)v, g), nc, pen);
    for (i = 0; i < nv; i++) printf(" %.10g", v[i]);
    printf("\n");
}

int main(void)
{
    static Erd g;
    cjitter_problem p; cjitter_budget b; cjitter_tuning t;
    double lo[64], hi[64], xh[64], xc[64], xbest[64], bestf;
    long i, k, m, s, nnew, nv;
    g.cw = ERD_CW; g.ch = ERD_CH; g.nfixed = ERD_NFIXED;
    nnew = ERD_NNEW; g.n = g.nfixed + nnew;
    for (i = 0; i < g.n; i++) { g.x[i]=erd_cx[i]; g.y[i]=erd_cy[i];
                               g.w[i]=erd_w[i]; g.h[i]=erd_h[i]; }
    g.ne = ERD_NEDGE;
    for (i = 0; i < g.ne; i++) { g.e[i][0]=erd_edge[i][0]; g.e[i][1]=erd_edge[i][1]; }
    { long deg[MAXN]={0}, seen[MAXN]={0};
      for (i=0;i<g.ne;i++){deg[g.e[i][0]]++;deg[g.e[i][1]]++;}
      for (i=0;i<g.ne;i++){
        g.ofr0[i]=((double)(seen[g.e[i][0]]++ +1)/(double)(deg[g.e[i][0]]+1)-0.5)*0.8;
        g.ofr1[i]=((double)(seen[g.e[i][1]]++ +1)/(double)(deg[g.e[i][1]]+1)-0.5)*0.8; } }
    g.straight = 0; g.konst = frozen_part(&g);
    nv = 2 * nnew;
    for (i = 0; i < nv; i += 2) { lo[i]=0; hi[i]=g.cw; lo[i+1]=0; hi[i+1]=g.ch; }
    p.n=nv; p.lo=lo; p.hi=hi; p.fitness=score; p.repair=legal; p.ctx=&g;
    b.evals=BUDGET; b.seed=1; b.jitter=JITTER; b.pop=POP;
    for (k = 0; k < nnew; k++) { xh[2*k]=erd_cx[g.nfixed+k]; xh[2*k+1]=erd_cy[g.nfixed+k]; }
    centroid_place(&g, xc); legal(xc, &g);
    printf("# pair %d nfixed %d nnew %d canvas %g %g\n", PAIR_ID, ERD_NFIXED, ERD_NNEW,
           (double)ERD_CW, (double)ERD_CH);
    dump("human", xh, nv, &g);
#ifdef DUMP_ROUTES
    dump_routes("human", xh, &g);
#endif
    {   /* Is the maintainer's placement a local minimum of S? Descend from it with the same
         * move the searches use and see how far the score falls. */
        double xl[64], cand[64], f, fc; long it, j, acc = 0; Rng rg;
        cjitter_rng_seed(&rg, 12345u);
        memcpy(xl, xh, sizeof xl); legal(xl, &g); f = score(xl, &g);
        for (it = 0; it < 200000; it++) {
            double sc = 40.0;
            memcpy(cand, xl, sizeof cand);
            for (j = 0; j < nv; j++) cand[j] += ((cjitter_rng_u32(&rg) / 4294967296.0) - 0.5) * 2.0 * sc;
            legal(cand, &g);
            fc = score(cand, &g);
            if (fc < f) { f = fc; memcpy(xl, cand, sizeof xl); acc++; }
        }
        printf("# local descent from the human placement: S %.10g -> %.10g in %ld accepted moves\n",
               score(xh, &g), f, acc);
        dump("human_descended", xl, nv, &g);
    }
    dump("centroid", xc, nv, &g);
    for (m = 0; cjitter_methods[m]; m++) {
        bestf = 1e300;
        for (s = 0; s < PANEL; s++) {
            cjitter_budget bb = b; cjitter_result r; double xv[64];
            memset(&r, 0, sizeof r); r.x = xv;
            bb.seed = 1u + 7919u * (uint32_t)s;
            t = cjitter_tuning_default(nv);
            if (cjitter_run_tuned(cjitter_methods[m], &p, &bb, &t, &r) != 0) return 1;
            if (r.best < bestf) { bestf = r.best; memcpy(xbest, xv, sizeof xbest); }
#ifdef DUMP_ALL
            { char tg[64]; sprintf(tg, "%s.%ld", cjitter_methods[m], s); dump(tg, xv, nv, &g); }
#endif
        }
        dump(cjitter_methods[m], xbest, nv, &g);
    }
    return 0;
}
