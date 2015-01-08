#!/bin/bash
pdoc --overwrite --all-submodules --html --html-dir /tmp/spockdocs ./spock
git checkout gh-pages
rm -rf ./docs
mv /tmp/spockdocs ./docs
git add -A
git commit -m "Updated docs"
git push
git checkout master
