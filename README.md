# The Unique Games Theorem: a short proof and a compressed presentation

[![Short proof DOI](https://img.shields.io/badge/short_proof-10.5281%2Fzenodo.23265572-154881)](https://doi.org/10.5281/zenodo.23265572)
[![Compressed presentation DOI](https://img.shields.io/badge/compressed_presentation-10.5281%2Fzenodo.23264902-154881)](https://doi.org/10.5281/zenodo.23264902)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--1341--366X-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0001-1341-366X)
[![Repository quality](https://github.com/lgboim/unique-games-short-proof/actions/workflows/repository-quality.yml/badge.svg)](https://github.com/lgboim/unique-games-short-proof/actions/workflows/repository-quality.yml)
[![Text: CC BY 4.0](https://img.shields.io/badge/text-CC_BY_4.0-lightgrey.svg)](LICENSE-DOCUMENTATION-DATA.txt)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE-CODE.txt)

Papers, LaTeX sources and Lean check logs for two expository preprints by Ariel Elboim on OpenAI's proof of the Unique Games Theorem:

> OpenAI (2026), *[The Unique Games Theorem](https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/paper.pdf)*. Preprint, 23 September 2026.

OpenAI's preprint gives a deterministic polynomial-time reduction from satisfiability to unique games that separates almost satisfiable games from games of small value. The first paper here gives a short proof of that theorem, self-contained apart from three earlier theorems stated as inputs, and simplifies several of the source's steps. The second follows the source closely and is reorganized for reading. `lean_check/` holds the script and logs of one run of the Comparator check of OpenAI's Lean 4 formalization of the source theorem; that check concerns OpenAI's formal development, not these papers. The construction and the main proof are OpenAI's. Both papers were prepared with AI models, and no human expert has reviewed them yet.

**Papers:** [Zenodo 10.5281/zenodo.23265572](https://doi.org/10.5281/zenodo.23265572) (short proof and companion note) · [Zenodo 10.5281/zenodo.23264902](https://doi.org/10.5281/zenodo.23264902) (compressed presentation and Lean check) · **author:** [ORCID 0009-0001-1341-366X](https://orcid.org/0009-0001-1341-366X), independent researcher

Both records were published on 9 October 2026 as Version 1.0. Zenodo holds the citable, immutable archives. This GitHub repository is the maintained working view and will carry documented corrections and later releases.

## Papers

| Paper | Pages | PDF | LaTeX | DOI |
| --- | --- | --- | --- | --- |
| **The Unique Games Theorem: A Short Self-Contained Proof** | 11 | [PDF](papers/ugc_short_proof.pdf) | [`.tex`](papers/ugc_short_proof.tex) | [10.5281/zenodo.23265572](https://doi.org/10.5281/zenodo.23265572) |
| Companion note: *Attribution, Provenance and Checks* | 3 | [PDF](papers/ugc_short_proof_companion_note.pdf) | [`.tex`](papers/ugc_short_proof_companion_note.tex) | same record, [10.5281/zenodo.23265572](https://doi.org/10.5281/zenodo.23265572) |
| **A Compressed Presentation of OpenAI's Proof of the Unique Games Theorem** | 17 | [PDF](papers/ugc_faithful_presentation.pdf) | [`.tex`](papers/ugc_faithful_presentation.tex) | [10.5281/zenodo.23264902](https://doi.org/10.5281/zenodo.23264902) |

Both papers are self-contained apart from three earlier theorems, stated as inputs: Håstad's parity gap, the Khot–Minzer–Safra Grassmann expansion theorem, and Dinur–Steurer projection-game repetition. They are written for a reader comfortable with finite-field linear algebra and Fourier analysis on finite groups.

## What the papers contain

The theorem: for every fixed 0 < ε, δ < 1/2, a deterministic polynomial-time reduction maps satisfiable formulas to unique games of value at least 1 − ε and unsatisfiable formulas to unique games of value at most δ. The games are explicit, unweighted and on simple bipartite graphs; the alphabet is a fixed binary vector space and every constraint is a translation.

The argument, as in the source, has four steps. It builds a nonlinear noise that rarely changes the honest labeling's output, yet any linear family that sees enough of the output notices it with constant probability. It extracts constant-output certificates from any labeling that the test accepts often. It decodes those certificates using only local information. And it contradicts parallel repetition on clean coordinates. A last section removes the weights and amplifies the gap.

The **short proof** simplifies several of these steps relative to the source:

- the noise gadget's recursion is written in direct coordinates, and the survival of linear rank is proved by one induction on the height;
- genericity is proved by formal differentiation;
- test acceptance is bounded directly by the measure of good row fibers, without recoloring or concentration;
- the second player guesses a constant output and Fourier-samples one row;
- a triangle of three equations replaces variable cloning.

Its [companion note](papers/ugc_short_proof_companion_note.pdf) lists every departure from the source, credits the contributors to each simplification, describes the review, and reports the Lean check.

The **compressed presentation** keeps the source's conditioning and parameter order. It modifies the root construction of the noise gadget, simplifies certificate extraction and rewrites the genericity proof. Its Attribution section, at the end of Section 6, lists these and smaller changes passage by passage. Appendix A reports the Lean check.

## Repository map

| Path | Purpose |
| --- | --- |
| [`papers/`](papers/) | The two papers and the companion note, as PDF and standalone LaTeX source, byte-identical to the Zenodo deposits |
| [`lean_check/ugc_lean_check.py`](lean_check/ugc_lean_check.py) | The script that ran the Comparator check of OpenAI's Lean 4 formalization |
| [`lean_check/ugc-lean-ugt-check.log`](lean_check/ugc-lean-ugt-check.log) | The complete log of that run |
| [`lean_check/ugc_out.zip`](lean_check/ugc_out.zip) | The run's output directory: per-phase logs, axioms, timings and summary |
| [`public_manifest.json`](public_manifest.json), [`verify_manifest.py`](verify_manifest.py) | SHA-256 inventory of every tracked file, and its checker |
| [`CITATION.cff`](CITATION.cff), [`codemeta.json`](codemeta.json) | Machine-readable citation and metadata |
| [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md) | Which licence covers which file |

## Quick verification

From the repository root, with Python 3 and no other packages:

```bash
python verify_manifest.py --check
```

This checks every tracked file against the SHA-256 inventory, and the nine files in `papers/` and `lean_check/` against the MD5 checksums that Zenodo reports for its deposits.

Each `.tex` file is standalone. Build it with [Tectonic](https://tectonic-typesetting.github.io/) into a separate directory, so that the deposited PDF is not overwritten:

```bash
tectonic -X compile --outdir build papers/ugc_short_proof.tex
tectonic -X compile --outdir build papers/ugc_short_proof_companion_note.tex
tectonic -X compile --outdir build papers/ugc_faithful_presentation.tex
```

A rebuilt PDF has the same content but is not byte-identical to the deposited one, since PDF metadata differs between builds.

## Research transparency

- **AI use.** Both papers were prepared with Codex (OpenAI), Claude (Anthropic) and other AI models. The companion note credits each model's contributions to the short proof.
- **Review.** Separate AI reviewers checked every step, and finite claims were checked by exact computation. These checks do not certify OpenAI's preprint or constitute formal verification of these papers.
- **No human review.** No human expert has reviewed either paper yet. Corrections are very welcome; see [`CONTRIBUTING.md`](CONTRIBUTING.md).
- **Lean check and its scope.** On 9 October 2026 we ran the Comparator check of OpenAI's Lean 4 formalization, at revision `fd4aeeb` of `openai/math`, with Lean 4.34.1. It passed: the kernel accepted `OAI.UniqueGamesTheorem.theorem11` with the axioms `propext`, `Classical.choice` and `Quot.sound`. The sandbox was not enforced, so the run lacked the isolation that Comparator recommends, and we did not audit whether the formal statement matches the papers' main theorem. The check concerns OpenAI's formal development. It does not check these papers, their simplifications or their other changes, and the papers are not derived from the formalization. Details are in Appendix A of [10.5281/zenodo.23264902](https://doi.org/10.5281/zenodo.23264902) and in the companion note.
- **Related exposition.** Lance Fortnow's earlier exposition presents the same proof at greater length. These papers were prepared independently of it.

## Citation

Use GitHub's **Cite this repository** control, the metadata in [`CITATION.cff`](CITATION.cff), or cite the immutable Zenodo releases:

> Elboim, A. (2026). *The Unique Games Theorem: A Short Self-Contained Proof* (Version 1.0). Zenodo. https://doi.org/10.5281/zenodo.23265572

> Elboim, A. (2026). *A Compressed Presentation of OpenAI's Proof of the Unique Games Theorem* (Version 1.0). Zenodo. https://doi.org/10.5281/zenodo.23264902

```bibtex
@misc{elboim2026ugcshort,
  author    = {Elboim, Ariel},
  title     = {The Unique Games Theorem: A Short Self-Contained Proof},
  year      = {2026},
  version   = {1.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.23265572},
  url       = {https://doi.org/10.5281/zenodo.23265572}
}
@misc{elboim2026ugcfaithful,
  author    = {Elboim, Ariel},
  title     = {A Compressed Presentation of {OpenAI}'s Proof of the Unique Games Theorem},
  year      = {2026},
  version   = {1.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.23264902},
  url       = {https://doi.org/10.5281/zenodo.23264902}
}
```

For the theorem and its original proof, cite OpenAI's preprint.

## Versioning and archival policy

- Zenodo Version 1.0 of both records (9 October 2026) is immutable and is the version to cite.
- The files in `papers/` and `lean_check/` are byte-identical to those deposits, and `verify_manifest.py --check` fails if one changes. They are not edited in place.
- A corrected paper will be released as a new Zenodo version under the same concept DOI ([10.5281/zenodo.23265571](https://doi.org/10.5281/zenodo.23265571) for the short proof, [10.5281/zenodo.23264901](https://doi.org/10.5281/zenodo.23264901) for the compressed presentation), and this repository will be updated to match.
- GitHub changes are documented in [`CHANGELOG.md`](CHANGELOG.md). Substantive releases will use semantic version tags and GitHub Releases.

## Licenses

The papers, their LaTeX sources, the Lean check logs and the documentation are licensed under [CC BY 4.0](LICENSE-DOCUMENTATION-DATA.txt), as declared on Zenodo. The scripts are licensed under the [MIT License](LICENSE-CODE.txt). The precise allocation is in [`LICENSE-SCOPE.md`](LICENSE-SCOPE.md).

## Questions and corrections

Mathematical errors, gaps, presentation problems and questions about the Lean check are welcome through [GitHub Issues](https://github.com/lgboim/unique-games-short-proof/issues). See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md) before opening an issue or pull request.
