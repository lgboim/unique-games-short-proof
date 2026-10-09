## Purpose

Describe the correction or improvement and the affected files.

## Checks

- [ ] No file in `papers/` or `lean_check/` was changed; they stay byte-identical to the Zenodo deposits.
- [ ] `python verify_manifest.py --write` was run and `python verify_manifest.py --check` passes.
- [ ] `CITATION.cff` and `codemeta.json` validate.
- [ ] No credentials, private paths, or non-public material are included.
- [ ] Documentation and `CHANGELOG.md` are updated where needed.

## Scope

State whether this changes documentation, metadata, templates, the workflow, `verify_manifest.py`, or licensing. Report mathematical errors as issues, not as pull requests against the papers.
