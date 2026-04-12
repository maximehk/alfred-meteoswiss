# MeteoSwiss Forecast — Alfred Workflow

Search Swiss local weather forecasts from [MeteoSwiss](https://www.meteoswiss.admin.ch) directly from Alfred 5, by postal code or place name.

## Usage

Trigger with the keyword `w` (configurable via the workflow variable `keyword`) followed by:

- **A postal code** — `w 8800` → Thalwil, Rüschlikon, …
- **A place name** — `w thalwil` → Thalwil (8800)

Press <kbd>Enter</kbd> on a result to open its local forecast in your browser.

The place-name search is fuzzy and diacritic-insensitive (`zurich` matches `Zürich`).

## Setup

The script uses [`uv`](https://docs.astral.sh/uv/) to manage its Python dependency ([Alfred-PyWorkflow](https://github.com/harrigan/Alfred-PyWorkflow)) automatically — no manual `pip install` required.

1. Install `uv`:
   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
2. Import the workflow into Alfred.
3. If `uv` is not found at runtime, edit the Script Filter and adjust `PATH`. Find your `uv` location with `which uv` — common locations are `~/.local/bin/uv` and `/opt/homebrew/bin/uv`.

Requires Python ≥ 3.9 (managed automatically by `uv`).

## How it works

- `meteoswiss.py` queries `https://www.meteoschweiz.admin.ch/static/resources/local-forecast-search/{prefix}.json`, where `{prefix}` is the first 1–2 characters of the query.
- The MeteoSwiss API returns all localities under that prefix as semicolon-delimited records, which are parsed into `id / canton / de / fr / it / en / zip / name / type` fields.
- Results for each prefix are cached for 1 hour via Alfred-PyWorkflow's `cached_data`. Queries longer than 2 characters filter the cached list locally and never hit the network, keeping the workflow fast and the MeteoSwiss servers happy.
- Numeric queries filter by postal code; text queries use a small custom fuzzy scorer that favours prefix and substring matches, then consecutive-character runs.
- Selecting a result opens `https://www.meteoswiss.admin.ch{en_path}#forecast-tab=detail-view` via the Open URL action.

## Files

- `meteoswiss.py` — Script Filter implementation
- `info.plist` — Alfred workflow definition
