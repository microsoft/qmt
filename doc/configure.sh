
rm -rf _build/* source/
sphinx-apidoc ../qmt -o source/
echo "Now run: make html"
