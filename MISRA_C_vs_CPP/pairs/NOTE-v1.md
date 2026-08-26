# v1 provenance
These 240 runs executed against gen-v1-as-run.py in this directory (reconstructed exactly by
reversing the v2 repairs; diff gen.py against it to see them): tmpl carried a
dead Key template parameter, mix's FileReader called std::exit, virt's
factories returned raw new, and the virt1 single-file pair did not exist.
The v2 rerun (7 pairs, repaired sides) replaces these numbers when it lands.
