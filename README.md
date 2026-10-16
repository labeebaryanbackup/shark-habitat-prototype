# Shark Habitat Prototype

A deterministic Python and Streamlit prototype for inspecting how
environmental variables flow into a shark-habitat suitability score.

This repository is a **learning prototype**, not a wildlife-tracking system, validated ecological model, or research product.

<p align="center">
  <img src="assets/temperature-response.svg" width="100%" alt="Unvalidated heuristic temperature-response curves for three example shark species">
</p>

The plot is generated from the current temperature-scoring function. It shows
how the software behaves for three example species; it is not an observation
dataset, an ecological benchmark, or evidence that sharks occupy a location.

<p align="center">
  <img src="assets/habitat-suitability.svg" width="100%" alt="Great white shark habitat-suitability heatmap over a generated 25x25 environmental grid, colored by unvalidated heuristic HSI">
</p>

This heatmap is the model's habitat-suitability (HSI) output over the same
generated grid. It shows the prototype's spatial behaviour for one example
species; it is not real shark habitat.

## What it currently demonstrates

- A Streamlit interface for selecting species and study settings
- Species-specific preference tables and heuristic suitability scoring
- Map and chart generation with pandas, NumPy, Plotly, and related tools
- An early workflow shaped around sea-surface temperature, chlorophyll, and bathymetry inputs
- An opt-in NASA CMR catalog lookup kept separate from the generated grids

## Important limits

- Environmental layers and habitat scores are **generated prototype inputs**, not satellite measurements or validated ecology — no live ingestion, no conservation claim.
- The workflow is reproducible (fixed seed `2339`); the optional NASA CMR lookup (`lookup_metadata=True`) adds a metadata search only, never turns grids into measurements.
- No live shark locations or presence claims; scores are not validated against tagged-animal observations, field surveys, or peer-reviewed benchmarks.

The former hard-coded telemetry example and pseudo-validation routine were
removed: generated locations and random error cannot measure ecological model
quality.

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The runtime dependency list contains only packages imported by the application or its optional data paths. TensorFlow, scikit-learn, and Matplotlib are not required.

Experimental authenticated NASA Earthdata requests require your own runtime token. See [NASA_TOKEN_SETUP.md](NASA_TOKEN_SETUP.md); the code reads only `EARTHDATA_TOKEN` and does not need a credential committed to the repository. The Streamlit workflow does not require a token, and a token does not turn the prototype into a live-data or validated system.

## Verify the checkout

The repository includes dependency-free checks for Python syntax and current-tree secret hygiene:

```bash
python -m compileall -q app.py automatic_nasa_framework.py tests
python -m unittest discover -s tests -v
```

GitHub Actions runs the same checks for every push and pull request.
It also installs the declared runtime dependencies, starts Streamlit, and checks the health endpoint.

After installing the runtime dependencies, rebuild or verify the README figures:

```bash
python tools/render_readme_assets.py
python tools/render_habitat_map.py
python tools/render_readme_assets.py --check
python tools/render_habitat_map.py --check
```

## License

The code is available under the [MIT License](LICENSE). Documentation and external datasets may have their own terms.

## Security note

NASA Earthdata credentials must be supplied at runtime through a local environment variable or another untracked secret store. Never place an access token in source code, examples, screenshots, issues, or commits.

Before any future public release that enables live ingestion:

1. rotate any credential that was previously committed through the provider;
2. decide separately whether to rewrite Git history;
3. add tests that distinguish real ingestion from simulated fallback data; and
4. record dataset names, timestamps, units, transformations, and failure modes.

## Sensible next steps

- Replace generated layers with a documented public dataset adapter
- Add deterministic fixtures and unit tests for every scoring component
- Compare scores against a named observation dataset
- Attach provenance and uncertainty to every map layer
- Review species parameters with a qualified marine scientist

Until those steps are complete, use this repository only as a software and visualization prototype.
