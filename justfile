[private]
default:
    @echo "Current tag: $(git describe --tags --abbrev=0 2>/dev/null || echo '(none)')"
    @echo ""
    @just --list

# Build the .alfredworkflow archive locally
[group('build')]
build:
    mkdir -p build
    zip -j build/MeteoSwiss.alfredworkflow info.plist meteoswiss.py icon.png

# Build and install into Alfred
[group('build')]
install: build
    open build/MeteoSwiss.alfredworkflow

# Run the script filter directly (e.g. just run 8001)
[group('dev')]
run query="":
    python3 meteoswiss.py "{{query}}"

# Open the GitHub repository in your browser
[group('dev')]
browse:
    open https://github.com/maximehk/alfred-meteoswiss

# Tag and push a release (e.g. just release 1.2.3)
[group('release')]
release version:
    git tag "v{{version}}"
    git push origin "v{{version}}"
