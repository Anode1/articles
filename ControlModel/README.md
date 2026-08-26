# Artifact Promotion as a Control Model

**Build once in a controlled environment and promote that same artifact through the
deployment environments, instead of building from source on each target machine.**

The central release question is not "did we build the latest code on production" but "which
approved artifact is deployed". The model separates five things that are usually mixed:
source code, build output, deployment approval, runtime configuration, and production
execution.

Environment-specific runtime data splits in two. True secrets are passwords, API tokens and
private keys. Operational configuration is database connection strings, SMTP hosts, internal
service URLs, bucket names, service identifiers and environment flags. Both are supplied at
runtime from an environment-scoped configuration set, never held in source control and never
embedded into the artifact. The separation limits the blast radius of a source-control
compromise, supports rollback and reproducibility, and produces the release evidence
expected in healthcare, finance, federal and defense systems.

| file | what it is |
| --- | --- |
| artifact_promotion_control_model.tex, .pdf | the control model, [doi:10.5281/zenodo.20451078](https://doi.org/10.5281/zenodo.20451078) |
| artifact_promotion_case_study.tex, .pdf | the implementation case study, [doi:10.5281/zenodo.20528904](https://doi.org/10.5281/zenodo.20528904) |
| ci_approaches.txt, argument_for_B_approach_over_A.txt | the working notes behind the comparison |
