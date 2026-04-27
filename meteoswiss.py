#!/usr/bin/env python3
"""MeteoSwiss local forecast search for Alfred 5."""

import sys
import json
import os
import time
import unicodedata
import urllib.request
import urllib.error

BASE_URL = "https://www.meteoschweiz.admin.ch/static/resources/local-forecast-search/{prefix}.json"
FORECAST_BASE = "https://www.meteoswiss.admin.ch"

FIELDS = ["id", "canton", "de", "fr", "it", "en", "_0", "zip", "_1", "name", "type"]


def parse_entry(raw):
    parts = raw.split(";")
    return dict(zip(FIELDS, parts))


def fetch_results(prefix):
    url = BASE_URL.format(prefix=prefix)
    req = urllib.request.Request(url, headers={"User-Agent": "Alfred-MeteoSwiss/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        return [parse_entry(r) for r in data]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return []
        raise


def _cache_dir():
    d = os.environ.get("alfred_workflow_cache", os.path.expanduser("~/.cache/alfred-meteoswiss"))
    os.makedirs(d, exist_ok=True)
    return d


def cached_data(key, fetch_fn, max_age):
    """Return cached data if fresh; call fetch_fn to refresh. max_age=0 means never expire."""
    path = os.path.join(_cache_dir(), key + ".json")
    if os.path.exists(path):
        if max_age == 0 or (time.time() - os.path.getmtime(path)) < max_age:
            with open(path) as f:
                return json.load(f)
    if fetch_fn is None:
        return None
    data = fetch_fn()
    with open(path, "w") as f:
        json.dump(data, f)
    return data


def _item(title, subtitle="", arg=None, valid=True, uid=None, copytext=None):
    item = {"title": title, "subtitle": subtitle, "valid": valid}
    if arg is not None:
        item["arg"] = arg
    if uid is not None:
        item["uid"] = uid
    if copytext is not None:
        item["text"] = {"copy": copytext}
    return item


def send_feedback(items):
    print(json.dumps({"items": items}))


def normalize(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def fuzzy_score(query, text):
    q = normalize(query)
    t = normalize(text)

    if q in t:
        return (100 + len(q) if t.startswith(q) else 80 + len(q)), True

    qi = 0
    last_pos = -1
    score = 0
    consecutive = 0

    for ti, ch in enumerate(t):
        if qi < len(q) and ch == q[qi]:
            if last_pos == ti - 1:
                consecutive += 1
                score += 10 + consecutive
            else:
                consecutive = 0
                score += 5
            last_pos = ti
            qi += 1

    if qi == len(q):
        score -= last_pos
        return max(1, score), True

    return 0, False


def main():
    query = sys.argv[1].strip() if len(sys.argv) > 1 else ""

    if not query:
        send_feedback([_item(
            "MeteoSwiss Forecast",
            "Type a Swiss postal code (e.g. 8800) or place name",
            valid=False,
        )])
        return

    prefix = query[:2] if len(query) >= 2 else query[:1]
    cache_key = "meteo_{}".format(prefix)

    if len(query) <= 2:
        try:
            entries = cached_data(cache_key, lambda: fetch_results(prefix), max_age=86400)
        except Exception as exc:
            send_feedback([_item("Error fetching data: {}".format(exc), valid=False)])
            return
    else:
        # Serve from cache only — never hit the network for long queries
        entries = cached_data(cache_key, None, max_age=0)

    if not entries:
        send_feedback([_item(
            'No results for "{}"'.format(query),
            "Type 1-2 digits first to load localities" if len(query) > 2 else "No Swiss localities found with this prefix",
            valid=False,
        )])
        return

    if query.isdigit():
        matches = sorted(
            [e for e in entries if e.get("zip", "").startswith(query)],
            key=lambda e: e.get("zip", ""),
        )
    else:
        scored = []
        for entry in entries:
            name = entry.get("name", "")
            canton = entry.get("canton", "")
            score, matched = fuzzy_score(query, name)
            if not matched:
                score, matched = fuzzy_score(query, "{} {}".format(name, canton))
            if matched:
                scored.append((score, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        matches = [e for _, e in scored]

    if not matches:
        send_feedback([_item('No results for "{}"'.format(query), valid=False)])
        return

    items = []
    for entry in matches:
        name = entry.get("name", "?")
        canton = entry.get("canton", "")
        zip_code = entry.get("zip", "")
        en_path = entry.get("en", "")
        url = FORECAST_BASE + en_path + "#forecast-tab=detail-view" if en_path else ""

        items.append(_item(
            title="{name}  ({zip})".format(name=name, zip=zip_code),
            subtitle="Canton {canton} — open MeteoSwiss local forecast".format(canton=canton),
            arg=url,
            valid=bool(url),
            uid=entry.get("id", name),
            copytext=url,
        ))

    send_feedback(items)


if __name__ == "__main__":
    main()
