#!/usr/bin/env python3
"""cat3.py: token count of category 3 for the endpoint experiment's Spring
side (Boot 3.3.4).

Category 3 is behavior fixed by version convention, in no source file of
the application. Its deciding text lives in the framework's documentation,
so the count uses the documentation sources at the exact git tags of the
BOM-resolved versions, the way category 2 used the sources jars: Antora
.adoc pages (Spring) and the javadoc-bearing feature enums (Jackson, whose
defaults have no reference manual). One row per convention on the
endpoint's path; where a page is broader than the rule, the stated ==
section is extracted (lower bound, matching the conservative category-2
trace). H2 itself is floor, as MySQL is elsewhere.

Emits cat3.json. Tokens are o200k via tiktoken.
"""
import json
import re
import urllib.request

import tiktoken

ENC = tiktoken.get_encoding("o200k_base")

FW = ("spring-projects/spring-framework", "v6.1.13",
      "framework-docs/modules/ROOT/pages/web/webmvc/mvc-controller/ann-methods/")
DJ = ("spring-projects/spring-data-jpa", "3.3.4",
      "src/main/antora/modules/ROOT/pages/")
# the keyword and definition pages of the JPA reference are include-stubs
# resolved from spring-data-commons at the same BOM version
DC = ("spring-projects/spring-data-commons", "3.3.4",
      "src/main/antora/modules/ROOT/pages/")
BOOT = ("spring-projects/spring-boot", "v3.3.4",
        "spring-boot-project/spring-boot-docs/src/docs/antora/modules/")
HIB = ("hibernate/hibernate-orm", "6.5.2",
       "documentation/src/main/asciidoc/userguide/chapters/domain/")
JACK = ("FasterXML/jackson-databind", "jackson-databind-2.17.2",
        "src/main/java/com/fasterxml/jackson/databind/")

# (convention on the endpoint's path, repo/tag/base, file, section or None)
ROWS = [
    ("@RequestParam binds by compiled Java parameter name",
     FW, "requestparam.adoc", None),
    ("@RequestBody deserialization of the POST body",
     FW, "requestbody.adoc", None),
    ("@ResponseBody serialization of return values",
     FW, "responsebody.adoc", None),
    ("derived-query grammar (findByAuthorOrderById, existsByToken)",
     DJ, "jpa/query-methods.adoc", None),
    ("repository query keywords",
     DC, "repositories/query-keywords-reference.adoc", None),
    ("repository interface semantics (Repository, declared save)",
     DC, "repositories/definition.adoc", None),
    ("a Filter @Component joins the servlet chain, order by convention",
     BOOT, "reference/pages/web/servlet.adoc",
     "Servlets, Filters, and Listeners"),
    ("DataSource auto-configured from H2 on the classpath",
     BOOT, "reference/pages/data/sql.adoc", "Embedded Database Support"),
    ("schema-all.sql initialization order vs Hibernate",
     BOOT, "how-to/pages/data-initialization.adoc", None),
    ("build compiled with -parameters by the Boot Gradle plugin",
     ("spring-projects/spring-boot", "v3.3.4",
      "spring-boot-project/spring-boot-tools/spring-boot-gradle-plugin/"
      "src/docs/antora/modules/gradle-plugin/pages/"),
     "reacting.adoc", None),
    ("implicit table and column naming",
     HIB, "naming.adoc", None),
    ("field access from @Id placement",
     HIB, "access.adoc", None),
    ("IDENTITY value generation",
     HIB, "identifiers.adoc", "Generated identifier values"),
    ("Jackson deserialization defaults (absent field, unknown field)",
     JACK, "DeserializationFeature.java", None),
    ("Jackson serialization defaults (inclusion, getter discovery)",
     JACK, "SerializationFeature.java", None),
]


def fetch(repo, tag, path):
    url = f"https://raw.githubusercontent.com/{repo}/{tag}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "cat3-measure"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8"), url


def section(text, title):
    """The == or === section whose heading contains title, to the next
    heading of the same or higher level."""
    m = re.search(rf"^(=+) [^\n]*{re.escape(title)}[^\n]*$", text,
                  re.M | re.I)
    if not m:
        raise SystemExit(f"section not found: {title}")
    level = len(m.group(1))
    rest = text[m.end():]
    n = re.search(rf"^={{2,{level}}} ", rest, re.M)
    return text[m.start():m.end() + (n.start() if n else len(rest))]


def main():
    out, total = [], 0
    for rule, (repo, tag, base), path, sec in ROWS:
        text, url = fetch(repo, tag, base + path)
        if sec:
            text = section(text, sec)
        tok = len(ENC.encode(text))
        total += tok
        out.append({"rule": rule, "url": url, "section": sec,
                    "lines": text.count("\n") + 1, "tokens": tok})
        print(f"{tok:7,}  {rule}" + (f"  [{sec}]" if sec else ""))
    print(f"{total:7,}  total")
    json.dump({"subject": "endpoint experiment, Spring Boot 3.3.4",
               "note": "documentation sources at the exact tags; "
                       "sections are lower bounds; H2 is floor",
               "rows": out, "total_tokens": total},
              open("cat3.json", "w"), indent=1)


if __name__ == "__main__":
    main()
