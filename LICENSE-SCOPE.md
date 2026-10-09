# Licence scope

## Papers, sources and logs: CC BY 4.0

The following files are licensed under Creative Commons Attribution 4.0 International, as described in `LICENSE-DOCUMENTATION-DATA.txt`:

- the two papers and the companion note under `papers/`, both the PDFs and their LaTeX sources;
- the Lean check logs `lean_check/ugc-lean-ugt-check.log` and `lean_check/ugc_out.zip`;
- the project documentation, citation metadata and `public_manifest.json`.

This matches the licence declared on both Zenodo records, [10.5281/zenodo.23265572](https://doi.org/10.5281/zenodo.23265572) and [10.5281/zenodo.23264902](https://doi.org/10.5281/zenodo.23264902).

## Scripts: MIT

The scripts `lean_check/ugc_lean_check.py` and `verify_manifest.py` are licensed under the MIT License in `LICENSE-CODE.txt`. Zenodo record 10.5281/zenodo.23264902 declares CC BY 4.0 for every file it holds, including its copy of `ugc_lean_check.py`. That script may therefore be used under either licence.

## Byte-identical copies of the Zenodo deposits

The nine files under `papers/` and `lean_check/` are byte-identical to the files deposited on Zenodo:

| Zenodo record | Files |
| --- | --- |
| [10.5281/zenodo.23265572](https://doi.org/10.5281/zenodo.23265572) | `papers/ugc_short_proof.pdf`, `papers/ugc_short_proof.tex`, `papers/ugc_short_proof_companion_note.pdf`, `papers/ugc_short_proof_companion_note.tex` |
| [10.5281/zenodo.23264902](https://doi.org/10.5281/zenodo.23264902) | `papers/ugc_faithful_presentation.pdf`, `papers/ugc_faithful_presentation.tex`, `lean_check/ugc_lean_check.py`, `lean_check/ugc-lean-ugt-check.log`, `lean_check/ugc_out.zip` |

`python verify_manifest.py --check` compares each of them with the MD5 checksum that Zenodo reports for it. They are not edited in this repository; corrections are released as new Zenodo versions.

## Third-party material

OpenAI's preprint *The Unique Games Theorem* and its Lean formalization, the works cited in the papers, and the tools named in the Lean check logs remain subject to their original terms. No rights in them are granted here.
