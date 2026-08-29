# Semantic Lifetime Width

Reproducible software companion for **When Can a Computation Forget? Semantic Lifetime Width and Query-Relative State Retirement**.

The repository implements the paper's exact finite constructions and audits under the corrected quotient-based definition of Semantic Lifetime Width (SLW). SLW is computed from the number of query-relative future-equivalence classes, not from raw historical bit counts. The package includes the pathwidth/SLW separating families, the same-structure two-query separation, certified expiring-history schedules, lifetime accounting, quotient-class state-volume calculations, explicit-enumeration microbenchmarks, regression tests, and an interactive Gradio laboratory.

## One-command reproduction

```bash
python -m pip install -r requirements.txt
python run_all.py
pytest -q
```

Generated tables are written to `results/tables`, figures to `results/figures`, and deterministic audit status to `results/summary.json`.

## GitHub Actions reproduction

The workflow in `.github/workflows/reproduce.yml` runs automatically on pushes and pull requests and can also be started manually with **Actions → Reproduce and test → Run workflow**. A successful run executes the tests, regenerates all results, writes the audit summary to the GitHub Actions job summary, and uploads a downloadable artifact named `semantic-lifetime-width-results-<run number>`. The artifact contains all generated CSV tables, PNG figures, and `results/summary.json` and is retained for 30 days.

## Interactive application

```bash
python app.py
```

The application has four laboratories: expiring-history dynamic programming, structural-width separation, two one-bit queries on the same sequential structure, and a quotient explorer that converts any chosen number of future-equivalence classes into SLW bits. The expiring-history tab also exposes the core-state factor required by the general complexity theorem.

## Reproducibility safeguards

The parity construction uses exactly two future-equivalence classes, corresponding to even and odd accumulated parity. The delayed indexed-bit construction uses `2^n` future classes before the index is revealed. Expiring-history state volume is computed as the sum of quotient-class counts, including the user-selected core-state multiplicity. Regression tests verify quotient-based SLW, lifetime double counting, both separating constructions, and the core-state factor.

The wall-clock enumeration benchmark is illustrative only; theorem claims use exact finite counts. No external dataset, human-participant data, stochastic inference, or network access is required for reproduction.

## Scientific scope

The project does not claim to solve P versus NP and does not present future equivalence, automata minimization, program slicing, abstract interpretation, pebbling, or graph width as new. The contribution investigated by the associated manuscript is the query-relative quotient-width parameter, its certified retirement calculus, its complexity consequences, and its structural/query separations.

## License

Apache-2.0.
