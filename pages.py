#!/usr/bin/env python3
"""Landing pages for the papers, one per paper beside its PDF, with the citation meta
tags Google Scholar reads, and a root index. Served by GitHub Pages from main at
https://anode1.github.io/articles/. Run from the repository root: python3 pages.py; --files lists what the
Pages workflow publishes."""
import html, os, re

BASE = "https://anode1.github.io/articles/"
REPO = "https://github.com/Anode1/articles/tree/main/"
AUTHOR = "Vasili Gavrilov"

PAPERS = [
 dict(dir="MISRA_C_vs_CPP", page="index.html", pdf="tokens_to_trace.pdf", abstract_md="Abstract.md",
      title="When Abstraction Becomes Indirection: Tokens-to-trace, measured on six stacks",
      date="2026/08/26", doi="10.5281/zenodo.22113993", group="papers",
      note="A shorter version is under review at IEEE Software."),
 dict(dir="cjitter", page="index.html", tex="stationary.tex", pdf="stationary.pdf",
      title="Layouts Made in Diagram Editors Are Held by Alignment and Flow, Not by Edge Length or Stress: A Per-Term Stationarity Test Before Fitting a Layout Energy",
      date="2026/09/05", doi="10.5281/zenodo.22313827", group="papers",
      extra_pdf=("stationary_supplement.pdf", "Supplement S1 to S8"), code="https://github.com/Anode1/cjitter"),
 dict(dir="smbpann", page="index.html", tex="emergence.tex", pdf="emergence.pdf",
      title="The Imposed and Emergent Pieces of Convolution Under an Energy Budget",
      date="2026/07/18", doi="10.5281/zenodo.21423177", group="papers", code="https://github.com/Anode1/SMBPANN",
      preprint="10.21203/rs.3.rs-10515959/v1",
      note="Under review at Genetic Programming and Evolvable Machines."),
 dict(dir="iac", page="index.html", tex="iac.tex", pdf="iac.pdf",
      title="A Wakeup, Not a Broker: The Minimal Transport for Coordinating Stateless LLM Agents",
      date="2026/07/05", doi="10.5281/zenodo.21206970", group="papers", code="https://github.com/Anode1/iac"),
 dict(dir="ais", page="index.html", tex="compress_the_access.tex", pdf="compress_the_access.pdf",
      title="Compress the Access, Not the Store: A Measurement of Key-Lookup versus File-Search Retrieval Cost for AI Agents, on a Real Engineering Project",
      date="2026/06/19", doi="10.5281/zenodo.20764255", group="papers", code="https://github.com/Anode1/ais"),
 dict(dir="ControlModel", page="index.html", tex="artifact_promotion_control_model.tex", pdf="artifact_promotion_control_model.pdf",
      title="Artifact Promotion as a Control Model for Stable Cloud Deployment: Build on Target Machines vs. Build Once and Promote Artifacts",
      date="2026/05/29", doi="10.5281/zenodo.20451077", group="papers"),
 dict(dir="ControlModel", page="case_study.html", tex="artifact_promotion_case_study.tex", pdf="artifact_promotion_case_study.pdf",
      title="The Artifact Promotion Control Model: An Implementation Case Study. Build on Target Machines vs. Build Once and Promote Artifacts",
      authors=[AUTHOR, "Enkli Ylli"], date="2026/06/03", doi="10.5281/zenodo.20528903", group="papers",
      arxiv="2609.35891"),
 dict(dir="agent_principal", page="index.html", tex="agent_principal.tex", pdf="agent_principal.pdf",
      title="The Agent as a Principal: What a Coding Agent Changes in the Chain from Commit to Production, and the Rule That Restores It",
      date="2026/10/15", doi="10.5281/zenodo.23402685", group="papers"),
 dict(dir="atree", page="index.html", tex="atree.tex", pdf="atree.pdf",
      title="The Atree Format: A Scalable Binary-Path Notation for Ancestral Genealogies, with an Application to Lineage Matching",
      date="2026/06/08", doi="10.5281/zenodo.20587715", group="papers"),
 dict(dir="ConditionalProbability", page="index.html", tex="conditional_probability.tex", pdf="conditional_probability.pdf",
      title="Conditional Probability in Diagnostic Testing: One Calculation in Four Notations, Tree, Bayes' Theorem, Contingency Table, and Likelihood Ratios, with the Clinical Risk Measures Read from the Same Table",
      date="2026/05/29", doi="10.5281/zenodo.20449608", group="papers"),
 dict(dir="innovation_compression", page="index.html", tex="innovation_compression.tex", pdf="innovation_compression.pdf",
      title="Chaos Makes Many, Compression Keeps Few: Where Innovation Comes From, and the Human Part",
      date="2026/06/09", doi="10.5281/zenodo.20603482", group="other"),
 dict(dir="intelligence_compressors", page="index.html", tex="intelligence_compressors.tex", pdf="intelligence_compressors.pdf",
      title="Intelligence Is the Discovery of Compressors",
      date="2026/05/29", doi="10.5281/zenodo.20440110", group="other"),
 dict(dir="BPFNN_Coursework", page="index.html", tex="coursework_1997_backprop_ffnn.tex", pdf="coursework_1997_backprop_ffnn.pdf",
      title="Backpropagation Feed-Forward Neural Networks (1997 Undergraduate Thesis, Revised Digital Edition 2026)",
      date="1997", online="2026/05/29", doi="10.5281/zenodo.20450525", group="other",
      thesis="The Open University of Israel", code="https://github.com/Anode1/bpnn"),
]

def detex(s):
    s = s.replace(r'\%', '\x00')
    s = re.sub(r'(?m)%.*$', '', s)
    s = s.replace('\x00', '%').replace(r'\noindent', '')
    s = re.sub(r'~?\\cite[pt]?\{[^}]*\}', '', s)
    s = re.sub(r'\\ref\{[^}]*\}', '', s)
    s = s.replace(r'\atree', 'Atree')
    for acc, ch in ((r'\"o', 'ö'), (r'\"a', 'ä'), (r'\"u', 'ü'), (r"\'e", 'é'), (r"\'o", 'ó')):
        s = s.replace(acc, ch).replace('{' + acc + '}', ch)
    for cmd in ('emph', 'textbf', 'textit', 'code', 'texttt', 'text', 'mathrm'):
        s = re.sub(r'\\' + cmd + r'\{([^{}]*)\}', r'\1', s)
    s = re.sub(r'\\' + 'large|\\small', '', s)
    s = s.replace(r'\times', '×').replace(r'\le', '≤').replace(r'\ge', '≥').replace(r'\approx', '≈')
    s = s.replace(r'\%', '%').replace(r'\,', ' ').replace(r'\;', ' ').replace(r'\&', '&').replace(r'\_', '_')
    s = s.replace('{,}', ',').replace('$', '').replace('~', ' ')
    s = s.replace('``', '“').replace("''", '”').replace('--', '–')
    s = re.sub(r'\\\\', ' ', s)
    s = re.sub(r'[{}]', '', s)
    s = re.sub(r'\s*×\s*', '×', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def abstract_of(p):
    d = p["dir"]
    if p.get("abstract_md"):
        return open(os.path.join(d, p["abstract_md"])).read().strip()
    tex = open(os.path.join(d, p["tex"])).read()
    m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S)
    return detex(m.group(1))

def meta(name, content):
    return f'  <meta name="{name}" content="{html.escape(content, quote=True)}">'

STYLE = ("body{max-width:42em;margin:2em auto;padding:0 1em;font:16px/1.5 Georgia,serif;color:#111;background:#fff}"
         "h1{font-size:1.4em;line-height:1.3}a{color:#1a4d8f}dl dt{font-weight:bold;margin-top:.6em}dl dd{margin:0}"
         "p.abstract{text-align:justify}footer{margin-top:3em;font-size:.9em;color:#555}")

def page(p):
    authors = p.get("authors", [AUTHOR])
    url = BASE + p["dir"] + "/" + ("" if p["page"] == "index.html" else p["page"])
    pdf_url = BASE + p["dir"] + "/" + p["pdf"]
    abstract = abstract_of(p)
    tags = [meta("citation_title", p["title"])]
    tags += [meta("citation_author", a) for a in authors]
    tags.append(meta("citation_publication_date", p["date"]))
    tags.append(meta("citation_online_date", p.get("online", p["date"])))
    tags.append(meta("citation_pdf_url", pdf_url))
    tags.append(meta("citation_abstract_html_url", url))
    tags.append(meta("citation_doi", p["doi"]))
    tags.append(meta("citation_language", "en"))
    if p.get("arxiv"):
        tags.append(meta("citation_arxiv_id", p["arxiv"]))
    if p.get("thesis"):
        tags.append(meta("citation_dissertation_institution", p["thesis"]))
    tags.append(meta("description", abstract[:300]))
    rows = [("Authors", ", ".join(authors)),
            ("Date", p["date"].replace("/", "-") if not p.get("online") else f'{p["date"]}; this edition {p["online"].replace("/", "-")}'),
            ("PDF", f'<a href="{p["pdf"]}">{p["pdf"]}</a>' + (f' and <a href="{p["extra_pdf"][0]}">{p["extra_pdf"][1]}</a>' if p.get("extra_pdf") else "")),
            ("Deposit", f'<a href="https://doi.org/{p["doi"]}">doi:{p["doi"]}</a> (Zenodo, all versions)')]
    if p.get("arxiv"):
        rows.append(("arXiv", f'<a href="https://arxiv.org/abs/{p["arxiv"]}">arXiv:{p["arxiv"]}</a>'))
    if p.get("preprint"):
        rows.append(("Preprint", f'<a href="https://doi.org/{p["preprint"]}">doi:{p["preprint"]}</a> (Research Square, In Review)'))
    if p.get("note"):
        rows.append(("Status", p["note"]))
    rows.append(("Sources, figures and data", f'<a href="{REPO + p["dir"]}">github.com/Anode1/articles/{p["dir"]}</a>'))
    if p.get("code"):
        rows.append(("Code", f'<a href="{p["code"]}">{p["code"].replace("https://", "")}</a>'))
    dl = "\n".join(f"  <dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(p["title"])}</title>
  <link rel="canonical" href="{url}">
{chr(10).join(tags)}
  <style>{STYLE}</style>
</head>
<body>
<h1>{html.escape(p["title"])}</h1>
<dl>
{dl}
</dl>
<h2>Abstract</h2>
<p class="abstract">{html.escape(abstract)}</p>
<footer><a href="../">All papers</a> · <a href="https://orcid.org/0009-0007-9371-5994">ORCID 0009-0007-9371-5994</a> · <a href="https://scholar.google.com/citations?user=7xlK2_gAAAAJ">Google Scholar</a></footer>
</body>
</html>
"""

def index():
    def item(p):
        href = p["dir"] + "/" + ("" if p["page"] == "index.html" else p["page"])
        year = p["date"][:4]
        authors = ", ".join(p.get("authors", [AUTHOR]))
        links = [f'<a href="https://doi.org/{p["doi"]}">doi:{p["doi"]}</a>', f'<a href="{p["dir"]}/{p["pdf"]}">PDF</a>']
        if p.get("arxiv"):
            links.append(f'<a href="https://arxiv.org/abs/{p["arxiv"]}">arXiv:{p["arxiv"]}</a>')
        if p.get("preprint"):
            links.append(f'<a href="https://doi.org/{p["preprint"]}">preprint doi:{p["preprint"]}</a>')
        return f'<li><a href="{href}">{html.escape(p["title"])}</a><br>{authors}, {year}. {" · ".join(links)}</li>'
    papers = "\n".join(item(p) for p in PAPERS if p["group"] == "papers")
    other = "\n".join(item(p) for p in PAPERS if p["group"] == "other")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Papers by Vasili Gavrilov</title>
  <link rel="canonical" href="{BASE}">
  <meta name="description" content="Papers by Vasili Gavrilov, with sources, figures, data and DOIs.">
  <style>{STYLE}li{{margin-bottom:.8em}}</style>
</head>
<body>
<h1>Papers by Vasili Gavrilov</h1>
<p>Each page carries the paper's PDF, its Zenodo DOI (the all-versions record) and a link to its
sources, figures and data in the <a href="https://github.com/Anode1/articles">articles</a> repository.
The catalog with venue and status is the <a href="https://github.com/Anode1">profile page</a>.</p>
<h2>Papers</h2>
<ul>
{papers}
</ul>
<h2>Other articles</h2>
<ul>
{other}
</ul>
<footer><a href="https://orcid.org/0009-0007-9371-5994">ORCID 0009-0007-9371-5994</a> · <a href="https://scholar.google.com/citations?user=7xlK2_gAAAAJ">Google Scholar</a></footer>
</body>
</html>
"""

def published_files():
    files = ["index.html", ".nojekyll"]
    for p in PAPERS:
        files += [p["dir"] + "/" + p["page"], p["dir"] + "/" + p["pdf"]]
        if p.get("extra_pdf"):
            files.append(p["dir"] + "/" + p["extra_pdf"][0])
    return files

if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--files"]:
        print("\n".join(published_files()))
        sys.exit(0)
    for p in PAPERS:
        assert os.path.exists(os.path.join(p["dir"], p["pdf"])), p["pdf"]
        open(os.path.join(p["dir"], p["page"]), "w").write(page(p))
    open("index.html", "w").write(index())
    open(".nojekyll", "w").close()
    print(len(PAPERS), "pages and index.html written")
