#!/usr/bin/env python3
"""closures.py: the four closure measurements of tokens_to_trace.tex.

Emits closures.json: per region, lines, exact characters, and o200k tokens.
Region lists are the manifests; the inclusion rule is in the paper. Roots are
overridable so the two public subjects can be re-fetched and re-measured:

  SYSTEM_A_ROOT   private tree (owner only; rows ship redacted)
  AIS_ROOT        github.com/Anode1/ais, c/ (default ~/ais/c)
  TASK_ROOT       taskwarrior v2.6.2, src/
  SPRING_ROOT     raeperd/realworld-springboot-java v2.1.1
  SPRING_FW_ROOT  extracted sources jars of the BOM-resolved versions

A missing root skips that system and keeps the others, so the public half is
reproducible without the private half.
"""
import json, os, sys

import tiktoken
ENC = tiktoken.get_encoding("o200k_base")

ROOTS = {
    "SYSTEM_A_ROOT": os.environ.get("SYSTEM_A_ROOT", ""),
    "AIS_ROOT": os.environ.get("AIS_ROOT", os.path.expanduser("~/ais/c")),
    "TASK_ROOT": os.environ.get("TASK_ROOT", os.path.expanduser("~/corpora/taskwarrior/src")),
    "SPRING_ROOT": os.environ.get("SPRING_ROOT", os.path.expanduser("~/corpora/realworld-springboot-java")),
    "SPRING_FW_ROOT": os.environ.get("SPRING_FW_ROOT", os.path.expanduser("~/corpora/spring-fw-src")),
    "MONO_ROOT": os.environ.get("MONO_ROOT", os.path.expanduser("~/corpora/monocypher")),
}

# (label, path, first_line, last_line); None lines = whole file.
# System A's manifest is private (the paper reports the system anonymously);
# closures.py loads it from SYSTEM_A_MANIFEST (default
# a private location) when present, and emits its rows with
# labels and counts only, no paths. Absent manifest = the public systems only.
SYSTEM_A = None
_mp = os.environ.get("SYSTEM_A_MANIFEST",
                     os.path.expanduser("~/.private/system_a_manifest.py"))
if os.path.exists(_mp):
    _ns = {}
    exec(open(_mp).read(), _ns)
    SYSTEM_A = _ns["SYSTEM_A"]

AIS_APP = [
 ("main.c grammar comment", "main.c", 1, 20),
 ("main.c get_ctx/print_value/on_id", "main.c", 49, 94),
 ("main.c collect_keys", "main.c", 165, 185),
 ("main.c resolve_project", "main.c", 230, 240),
 ("main.c do_get", "main.c", 309, 317),
 ("main.c option parse + index open", "main.c", 385, 547),
 ("main.c recall dispatch tail", "main.c", 1044, 1061),
 ("locate.c ais_locate", "locate.c", 398, 452),
 ("secret.c is_marked + reveal_context", "secret.c", 30, 56),
 ("doc.c ais_doc_is_blob", "doc.c", 298, 301),
 ("ais.h used declarations a", "ais.h", 1, 66),
 ("ais.h used declarations b", "ais.h", 99, 104),
 ("ais.h get/record contract", "ais.h", 234, 261),
 ("store.h on-disk format comment", "store.h", 1, 15),
]

AIS_REVEAL = [
 ("secret.c wipe/relpath", "secret.c", 24, 56),
 ("secret.c decrypt + helpers", "secret.c", 84, 241),
 ("secret.c secret_reveal", "secret.c", 243, 312),
 ("crypto contract ais_crypto.h", "crypto/ais_crypto.h", None, None),
]

AIS_ENGINE = [
 ("ais.c open/close/on_discard", "ais.c", 45, 71),
 ("ais.c ais_get", "ais.c", 1754, 1779),
 ("ais.c record_seek + ais_record", "ais.c", 1817, 1848),
 ("merge.c whole", "merge.c", None, None),
 ("post.c posting path", "post.c", 1, 60),
 ("post.c open/next/close", "post.c", 186, 232),
 ("key.c whole", "key.c", None, None),
 ("store.c store_open", "store.c", 291, 353),
 ("store.c store_close", "store.c", 371, 381),
 ("store.c store_each_record", "store.c", 523, 547),
 ("store.c off_get", "store.c", 646, 675),
 ("store.c store_value_at", "store.c", 677, 707),
 ("store.c multi_contains", "store.c", 758, 778),
 ("compact.c tomb_contains", "compact.c", 51, 72),
 ("store.h whole", "store.h", None, None),
 ("common.h whole", "common.h", None, None),
 ("post.h whole", "post.h", None, None),
 ("merge.h whole", "merge.h", None, None),
 ("key.h whole", "key.h", None, None),
]

# taskwarrior `task list`: whole files after static resolution of the two
# registries (Context::createDefaultConfig names report.list.columns; the
# command registry binds `list` to CmdCustom at its registration site).
_T_CORE = ["main.cpp","main.h","Context.cpp","Context.h","CLI2.cpp","CLI2.h",
 "Filter.cpp","Filter.h","Eval.cpp","Eval.h","Variant.cpp","Variant.h",
 "Lexer.cpp","Lexer.h","DOM.cpp","DOM.h","Task.cpp","Task.h",
 "sort.cpp","ViewTask.cpp","ViewTask.h","rules.cpp","feedback.cpp",
 "recur.cpp","dependency.cpp","legacy.cpp","util.cpp","util.h",
 "Hooks.cpp","Hooks.h"]
_T_STORE = ["TDB2.cpp","TDB2.h","libshared/src/FS.cpp","libshared/src/FS.h"]
_T_CMD = ["commands/Command.cpp","commands/Command.h",
          "commands/CmdCustom.cpp","commands/CmdCustom.h"]
_T_COLS = ["Column","ColTypeDate","ColTypeDuration","ColTypeNumeric",
 "ColTypeString","ColID","ColStart","ColEntry","ColDepends","ColUDA",
 "ColProject","ColTags","ColRecur","ColScheduled","ColDue","ColUntil",
 "ColDescription","ColUrgency"]
_T_SHARED = ["Configuration","Datetime","Duration","Color","Table","format",
 "shared","unicode","utf8","RX","Pig","Timer"]
TASK = ([("core: "+f, f, None, None) for f in _T_CORE]
      + [("store: "+f, f, None, None) for f in _T_STORE]
      + [("cmd: "+f, f, None, None) for f in _T_CMD]
      + [(f"col: {c}.{e}", f"columns/{c}.{e}", None, None)
         for c in _T_COLS for e in ("cpp","h")]
      + [(f"libshared: {s}.{e}", f"libshared/src/{s}.{e}", None, None)
         for s in _T_SHARED for e in ("cpp","h")]
      + [("libshared: wcwidth.h", "libshared/src/wcwidth.h", None, None)])

# Monocypher 4.0.3 (third-party, monocypher.org): the AEAD encrypt path,
# crypto_aead_lock, wire to bytes: XChaCha20 keystream + Poly1305 tag.
MONO = [
 ("macros, types, zero buffer", "monocypher.c", 63, 90),
 ("load/store/rotl helpers", "monocypher.c", 100, 142),
 ("crypto_wipe", "monocypher.c", 164, 177),
 ("chacha20 rounds + constant", "monocypher.c", 179, 203),
 ("crypto_chacha20_h", "monocypher.c", 205, 219),
 ("crypto_chacha20_djb", "monocypher.c", 220, 278),
 ("crypto_chacha20_x", "monocypher.c", 288, 299),
 ("poly1305 blocks/init/update/final", "monocypher.c", 311, 442),
 ("lock_auth", "monocypher.c", 2890, 2906),
 ("crypto_aead_init_x", "monocypher.c", 2907, 2914),
 ("crypto_aead_write", "monocypher.c", 2931, 2961),
 ("crypto_aead_lock", "monocypher.c", 2963, 2972),
 ("header contract (whole)", "monocypher.h", None, None),
]

_S = "src/main/java/io/github/raeperd/realworld/"
SPRING_CAT1 = [
 ("ArticleRestController list region", _S+"application/article/ArticleRestController.java", 1, 56),
 ("ArticleService header+ctor", _S+"domain/article/ArticleService.java", 1, 28),
 ("ArticleService getArticlesByAuthorName", _S+"domain/article/ArticleService.java", 62, 66),
 ("ArticleRepository", _S+"domain/article/ArticleRepository.java", None, None),
 ("Article entity", _S+"domain/article/Article.java", None, None),
 ("ArticleContents entity", _S+"domain/article/ArticleContents.java", None, None),
 ("ArticleTitle entity", _S+"domain/article/ArticleTitle.java", None, None),
 ("Tag entity", _S+"domain/article/tag/Tag.java", None, None),
 ("User entity", _S+"domain/user/User.java", None, None),
 ("Profile entity", _S+"domain/user/Profile.java", None, None),
 ("UserName embeddable", _S+"domain/user/UserName.java", None, None),
 ("MultipleArticleModel", _S+"application/article/MultipleArticleModel.java", None, None),
 ("ArticleModel", _S+"application/article/ArticleModel.java", None, None),
 ("ProfileModel", _S+"application/user/ProfileModel.java", None, None),
 ("SecurityConfiguration", _S+"application/security/SecurityConfiguration.java", None, None),
 ("JWTAuthenticationFilter", _S+"application/security/JWTAuthenticationFilter.java", None, None),
 ("HmacSHA256JWTService", _S+"infrastructure/jwt/HmacSHA256JWTService.java", None, None),
 ("HmacSHA256", _S+"infrastructure/jwt/HmacSHA256.java", None, None),
 ("Base64URL", _S+"infrastructure/jwt/Base64URL.java", None, None),
 ("UserJWTPayload", _S+"infrastructure/jwt/UserJWTPayload.java", None, None),
 ("JWTPayload iface", _S+"domain/jwt/JWTPayload.java", None, None),
 ("JWTDeserializer iface", _S+"domain/jwt/JWTDeserializer.java", None, None),
 ("JWTConfiguration", _S+"infrastructure/jwt/JWTConfiguration.java", None, None),
 ("WebMvcConfiguration", _S+"application/WebMvcConfiguration.java", None, None),
 ("RealWorldApplication", _S+"RealWorldApplication.java", None, None),
 ("application.properties", "src/main/resources/application.properties", None, None),
 ("schema.sql", "src/main/resources/schema.sql", None, None),
 ("build.gradle versions block", "build.gradle", 1, 40),
]

SPRING_CAT2 = [
 "spring-webmvc-7.0.8/org/springframework/web/servlet/DispatcherServlet.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/handler/AbstractHandlerMethodMapping.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/mvc/method/RequestMappingInfo.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/mvc/condition/ParamsRequestCondition.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerMapping.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/mvc/method/annotation/RequestMappingHandlerAdapter.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/mvc/method/annotation/ServletInvocableHandlerMethod.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/mvc/method/annotation/RequestResponseBodyMethodProcessor.java",
 "spring-webmvc-7.0.8/org/springframework/web/servlet/mvc/method/annotation/AbstractMessageConverterMethodProcessor.java",
 "spring-web-7.0.8/org/springframework/web/method/support/InvocableHandlerMethod.java",
 "spring-web-7.0.8/org/springframework/web/method/annotation/RequestParamMethodArgumentResolver.java",
 "spring-web-7.0.8/org/springframework/http/converter/json/JacksonJsonHttpMessageConverter.java",
 "spring-web-7.0.8/org/springframework/http/converter/AbstractJacksonHttpMessageConverter.java",
 "spring-security-web-7.1.0/org/springframework/security/web/FilterChainProxy.java",
 "spring-security-web-7.1.0/org/springframework/security/web/context/SecurityContextHolderFilter.java",
 "spring-security-web-7.1.0/org/springframework/security/web/authentication/AnonymousAuthenticationFilter.java",
 "spring-security-web-7.1.0/org/springframework/security/web/access/intercept/AuthorizationFilter.java",
 "spring-security-config-7.1.0/org/springframework/security/config/annotation/web/builders/HttpSecurity.java",
 "spring-security-core-7.1.0/org/springframework/security/core/context/SecurityContextHolder.java",
 "spring-data-commons-4.1.0/org/springframework/data/web/PageableHandlerMethodArgumentResolver.java",
 "spring-data-commons-4.1.0/org/springframework/data/repository/query/parser/PartTree.java",
 "spring-data-commons-4.1.0/org/springframework/data/repository/query/parser/Part.java",
 "spring-data-commons-4.1.0/org/springframework/data/repository/core/support/RepositoryFactorySupport.java",
 "spring-data-commons-4.1.0/org/springframework/data/repository/core/support/QueryExecutorMethodInterceptor.java",
 "spring-data-jpa-4.1.0/org/springframework/data/jpa/repository/query/PartTreeJpaQuery.java",
 "spring-data-jpa-4.1.0/org/springframework/data/jpa/repository/query/JpaQueryCreator.java",
 "spring-data-jpa-4.1.0/org/springframework/data/jpa/repository/support/SimpleJpaRepository.java",
]


VERSIONS = {
    "TASK_ROOT": "taskwarrior v2.6.2",
    "SPRING_ROOT": "realworld-springboot-java v2.1.1",
    "SPRING_FW_ROOT": "sources jars, spring-boot-dependencies 4.1.0 BOM",
    "MONO_ROOT": "Monocypher 4.0.3",
    "AIS_ROOT": "ais head",
    "SYSTEM_A_ROOT": "System A private tree",
}


def gitrev(root):
    import subprocess
    r = subprocess.run(["git", "-C", root, "rev-parse", "--short", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() or None


def measure(root, manifest, redact=False):
    rows, missing, seen_paths = [], 0, set()
    for label, rel, a, b in manifest:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            missing += 1
            continue
        text = open(p, errors="replace").read()
        if a is not None:
            text = "\n".join(text.split("\n")[a - 1:b])
            lines = b - a + 1
        else:
            lines = text.count("\n")
        row = {"region": label, "path": rel, "from": a, "to": b,
               "lines": lines, "chars": len(text),
               "o200k": len(ENC.encode(text))}
        seen_paths.add(rel)
        if redact:
            row = {"region": label, "lines": row["lines"],
                   "chars": row["chars"], "o200k": row["o200k"]}
        rows.append(row)
    total = {"commit": gitrev(root), "version": None,
             "lines": sum(r["lines"] for r in rows),
             "chars": sum(r["chars"] for r in rows),
             "o200k": sum(r["o200k"] for r in rows),
             "files": len(seen_paths),
             "regions": len(rows), "missing": missing}
    return {"rows": rows, "total": total}


def treesize(root):
    """Whole-tree o200k for a source tree kept as context, not closure."""
    n = 0
    for dp, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".java"):
                n += len(ENC.encode(open(os.path.join(dp, f), errors="replace").read()))
    return n


def stamp(entry, key):
    entry["total"]["version"] = VERSIONS.get(key)
    return entry


def main():
    out = {"note": "tokens_to_trace.tex closure manifests; o200k via tiktoken"}
    a = ROOTS["SYSTEM_A_ROOT"]
    if SYSTEM_A is not None and a and os.path.isdir(a):
        out["system_a_endpoint"] = stamp(measure(a, SYSTEM_A, redact=True),
                                         "SYSTEM_A_ROOT")
    c = ROOTS["AIS_ROOT"]
    if os.path.isdir(c):
        out["ais_recall_app"] = stamp(measure(c, AIS_APP), "AIS_ROOT")
        out["ais_recall_reveal_branch"] = measure(c, AIS_REVEAL)
        out["ais_recall_engine"] = measure(c, AIS_ENGINE)
        full = [r for r in AIS_APP if r[0] != "store.h on-disk format comment"] + AIS_ENGINE
        out["ais_recall_full"] = measure(c, full)
        wf = sorted({r[1] for r in full})
        out["ais_recall_wholefile"] = measure(c, [(p, p, None, None) for p in wf])
    t = ROOTS["TASK_ROOT"]
    if t and os.path.isdir(t):
        out["taskwarrior_list"] = stamp(measure(t, TASK), "TASK_ROOT")
        nostore = [r for r in TASK if not r[0].startswith("store: ")]
        out["taskwarrior_list_store_as_floor"] = measure(t, nostore)
    s = ROOTS["SPRING_ROOT"]
    if s and os.path.isdir(s):
        out["spring_articles_cat1"] = stamp(measure(s, SPRING_CAT1), "SPRING_ROOT")
    f = ROOTS["SPRING_FW_ROOT"]
    if f and os.path.isdir(f):
        out["spring_articles_cat2"] = stamp(measure(
            f, [(os.path.basename(p), p, None, None) for p in SPRING_CAT2]),
            "SPRING_FW_ROOT")
        hib = os.path.join(f, "hibernate-core-7.4.1.Final")
        if os.path.isdir(hib):
            out["hibernate_core_total_o200k"] = treesize(hib)
    mr = ROOTS["MONO_ROOT"]
    if os.path.isdir(mr):
        out["monocypher_aead_lock"] = stamp(measure(mr, MONO), "MONO_ROOT")
    pg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pairs")
    if os.path.exists(os.path.join(pg, "gen.py")):
        import sys as _sys
        _sys.path.insert(0, pg)
        import gen as _gen
        pc = {}
        for _p in _gen.PAIRS:
            c = sum(len(ENC.encode(v)) for k, v in _gen.build(_p, "c").items()
                    if k.endswith((".c", ".h")))
            q = sum(len(ENC.encode(v)) for k, v in _gen.build(_p, "cpp").items()
                    if k.endswith((".cpp", ".h")))
            pc[_p] = {"c_o200k": c, "cpp_o200k": q}
        pc["total"] = {"c_o200k": sum(v["c_o200k"] for v in pc.values()),
                       "cpp_o200k": sum(v["cpp_o200k"] for v in pc.values())}
        out["pairs_closures_behavior_matched"] = pc
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "closures.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for k, v in out.items():
        if isinstance(v, dict) and "total" in v and "regions" in v.get("total", {}):
            t = v["total"]
            print(f"{k:34} {t['regions']:>3} regions {t['files']:>3} files "
                  f"{t['lines']:>6} lines {t['o200k']:>7} o200k"
                  + (f"  ({t['missing']} missing)" if t["missing"] else ""))


if __name__ == "__main__":
    main()
