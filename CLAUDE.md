# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**hdx-scraper-unep** collects Protected and Conserved Areas (WDPCA) data from the [UNEP-WCMC ArcGIS FeatureServer](https://data-gis.unep-wcmc.org/server/rest/services/ProtectedPlanet/WDPCA/FeatureServer) and publishes one HDX dataset per country.

## Commands

Install dependencies:
```bash
uv sync
```

Run the scraper:
```bash
uv run python -m hdx.scraper.unep
```

Run tests:
```bash
uv run pytest
```

Run a single test:
```bash
uv run pytest tests/test_pipeline.py
```

Lint check:
```bash
pre-commit run --all-files
```

## Architecture

The pipeline flows through two stages in `__main__.py`:

1. **`Pipeline.get_netadata`** — Queries the ArcGIS FeatureServer metadata endpoint to discover layers (points vs. polygons) and collects the union of ISO3 country codes across all layers.

2. **`Pipeline.generate_dataset`** — For each country, downloads each layer's features via ArcGIS query, writes a GPKG (all layers), per-layer GeoJSON and CSV, and attaches ArcGIS GeoService links. Returns an HDX `Dataset`.

### Key design points

- **One dataset per country**: iterates over ISO3 codes from `get_netadata` and creates/updates one HDX dataset each.
- **`Retrieve`** (`hdx-python-utilities`) abstracts HTTP downloads and supports save/replay via `save=True`/`use_saved=True` — used in tests to replay fixture data from `tests/fixtures/input/`.
- **GeoDataFrame via geopandas**: spatial data is read with `geopandas.read_file("ESRIJSON:...")` and written to GPKG, GeoJSON, and CSV resources.
- **Static config inside the package**: `config/` lives under `src/hdx/scraper/unep/config/` so it is installed with the package and located via `script_dir_plus_file`.

### Config files

- `src/hdx/scraper/unep/config/project_configuration.yaml` — ArcGIS FeatureServer URL, base filename, and tags
- `src/hdx/scraper/unep/config/hdx_dataset_static.yaml` — Static HDX metadata applied to every dataset (license, methodology, source, etc.)

## Environment

Requires `~/.hdx_configuration.yaml` with HDX credentials, or env vars: `HDX_KEY`, `HDX_SITE`, `USER_AGENT`, `TEMP_DIR`, `LOG_FILE_ONLY`.

Requires `~/.useragents.yaml` with an `hdx-scraper-unep` entry.

## Collaboration Style

- Be objective, not agreeable. Act as a partner, not a sycophant. Push back when you disagree, flag tradeoffs honestly, and don't sugarcoat problems.
- Keep explanations brief and to the point.
- Don't rely on recalled knowledge for facts that could be stale (API behaviour, library versions, external systems). Search or read the actual source first.

## Scope of Changes

When fixing a bug or addressing PR feedback, change only what is necessary to resolve the specific issue. Do not refactor surrounding code, rename variables, adjust formatting, or make improvements in the same commit unless they are directly required by the fix.
