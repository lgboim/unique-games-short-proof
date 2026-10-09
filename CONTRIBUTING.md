# Contributing

Reports of mathematical errors and gaps are the most valuable contribution to this repository. No human expert has reviewed these papers yet, so a careful reading that finds a problem matters more than anything else here. Presentation fixes and questions about the Lean check are also welcome.

## Before opening an issue

- Read `README.md` and, for the short proof, its companion note. The companion note and the compressed presentation's Attribution section list every departure from OpenAI's source proof.
- Check existing issues for the same point.
- Do not upload credentials, private paths or other non-public material.

## Reporting a mathematical error

Use the **Mathematical error** issue template. A useful report gives:

- **the paper**: the short proof, its companion note, or the compressed presentation;
- **the location**: section, and the theorem, lemma or equation number, with the page and line where possible;
- **the claim**, quoted or restated as the paper writes it;
- **the problem**: a counterexample, or the step that does not follow and why;
- **its origin**, if you know it: whether the step is inherited from OpenAI's source proof or is one of the departures listed in the companion note or under Attribution. An error in a departure affects these papers only; an error in an inherited step may also concern the source.

A suspected gap is worth reporting even without a counterexample. Say what is missing and what would close it.

Typos, unclear passages, wrong cross-references and broken links go in the **Presentation or typo** template. Questions about the Comparator run go in the **Reproduction of the Lean check** template. That check concerns OpenAI's Lean formalization, not these papers.

## Pull requests

The files in `papers/` and `lean_check/` are byte-identical to the Zenodo deposits and are not edited in place. A correction to a paper is made by the author in a new Zenodo version, after which this repository is updated. Please report the error as an issue rather than as a pull request against a `.tex` file.

Pull requests are welcome for the README, the other documentation, the metadata, the templates, the workflow and `verify_manifest.py`. Keep them narrowly scoped and say what they change. Before submitting, run:

```bash
python verify_manifest.py --write
python verify_manifest.py --check
python -m json.tool codemeta.json >/dev/null
python -c "import yaml; yaml.safe_load(open('CITATION.cff', encoding='utf-8'))"
```

A change to any tracked file must be followed by `python verify_manifest.py --write`, so that `public_manifest.json` stays current. Document the change in `CHANGELOG.md`.

By contributing, you agree that code contributions are licensed under MIT and documentation contributions under CC BY 4.0, consistent with `LICENSE-SCOPE.md`.
