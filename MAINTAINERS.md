#  Maintainer notes

## Releasing

Releases are produced by the `Release` GitHub Actions workflow (`.github/workflows/release.yml`), which is triggered by pushing a tag matching `v*`. The workflow sets the `info.plist` version from the tag name, zips `info.plist` and `meteoswiss.py` into `MeteoSwiss.alfredworkflow`, and publishes a GitHub Release with auto-generated notes.

To cut a new release:

```sh
git tag v0.0.1
git push origin v0.0.1
```

Use semver (`vMAJOR.MINOR.PATCH`). The leading `v` is stripped before being written into `info.plist`.
