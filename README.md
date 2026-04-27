# MeteoSwiss Forecast — Alfred Workflow

<img src="icon.png" alt="MeteoSwiss icon" width="128" align="right" />

Search Swiss local weather forecasts from [MeteoSwiss](https://www.meteoswiss.admin.ch) directly from Alfred 5, by postal code or place name.

## Install

Download the latest [`MeteoSwiss.alfredworkflow`](https://github.com/maximehk/alfred-meteoswiss/releases/latest) and double-click to import into Alfred.

## Usage

Trigger with the keyword `weather` (configurable in the workflow's Configure panel) followed by:

- **A postal code** — `weather 8001` → Zürich, …
- **A place name** — `weather basel` → Basel (4001)

Press <kbd>Enter</kbd> on a result to open its local forecast in your browser.

The place-name search is fuzzy and diacritic-insensitive (`zurich` matches `Zürich`).

## Setup

No dependencies — the script uses only the Python 3 standard library, which ships with macOS. Just import the workflow and go.

## How it works

- `meteoswiss.py` queries `https://www.meteoschweiz.admin.ch/static/resources/local-forecast-search/{prefix}.json`, where `{prefix}` is the first 1–2 characters of the query.
- The MeteoSwiss API returns all localities under that prefix as semicolon-delimited records, which are parsed into `id / canton / de / fr / it / en / zip / name / type` fields.
- Results for each prefix are cached for 1 day to `$alfred_workflow_cache` (falling back to `~/.cache/alfred-meteoswiss`). Queries longer than 2 characters filter the cached list locally and never hit the network, keeping the workflow fast and the MeteoSwiss servers happy.
- Numeric queries filter by postal code; text queries use a small custom fuzzy scorer that favours prefix and substring matches, then consecutive-character runs.
- Selecting a result opens `https://www.meteoswiss.admin.ch{en_path}#forecast-tab=detail-view` via the Open URL action.

## Files

- `meteoswiss.py` — Script Filter implementation
- `info.plist` — Alfred workflow definition
