# The Unique Games Theorem: a short proof and a faithful presentation

Two expository preprints on OpenAI's proof of the Unique Games Conjecture ([OpenAI, "The Unique Games Theorem", 23 September 2026](https://github.com/openai/math/blob/main/preprints/The-Unique-Games-Theorem-September-23-2026/paper.pdf)).

| Paper | Pages | PDF | DOI |
|---|---|---|---|
| **The Unique Games Theorem: A Short Self-Contained Proof** | 11 (+ 3-page companion note) | [papers/ugc_short_proof.pdf](papers/ugc_short_proof.pdf) | [10.5281/zenodo.23265572](https://doi.org/10.5281/zenodo.23265572) |
| **A Compressed Presentation of OpenAI's Proof of the Unique Games Theorem** | 17 | [papers/ugc_faithful_presentation.pdf](papers/ugc_faithful_presentation.pdf) | [10.5281/zenodo.23264902](https://doi.org/10.5281/zenodo.23264902) |

Both are self-contained apart from three earlier theorems, stated as inputs: Håstad's parity gap, the Khot–Minzer–Safra Grassmann expansion theorem, and Dinur–Steurer projection-game repetition.

- The **short proof** simplifies several steps of the source. Every departure from the source, with credits, is listed in the [companion note](papers/ugc_short_proof_companion_note.pdf).
- The **faithful presentation** follows OpenAI's argument closely, reorganized for reading. Its Attribution section lists the few places where it departs from the source.

## Status

Both papers were prepared with Codex (OpenAI), Claude (Anthropic) and other AI models, and every step was checked by separate AI reviewers. Finite claims were also checked by exact computation. No human expert has reviewed them yet, so corrections are very welcome: please open an issue.

## Lean check

`lean_check/` holds the script and complete logs of our run of the Comparator check on OpenAI's Lean 4 formalization of the source theorem, on 9 October 2026 with Lean 4.34.1. Comparator passed, and the kernel accepted `OAI.UniqueGamesTheorem.theorem11` with the axioms `propext`, `Classical.choice` and `Quot.sound`. This check concerns OpenAI's formal development. It does not check these papers. Details are in Appendix A of the faithful presentation.

## Building

Each `.tex` file is standalone. Build it with `tectonic -X compile <file>.tex`.

## Citation

```bibtex
@misc{elboim2026ugcshort,
  author = {Elboim, Ariel},
  title  = {The Unique Games Theorem: A Short Self-Contained Proof},
  year   = {2026},
  doi    = {10.5281/zenodo.23265572}
}
@misc{elboim2026ugcfaithful,
  author = {Elboim, Ariel},
  title  = {A Compressed Presentation of OpenAI's Proof of the Unique Games Theorem},
  year   = {2026},
  doi    = {10.5281/zenodo.23264902}
}
```

## License

The papers and their sources are licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The script in `lean_check/` is under the MIT License.
