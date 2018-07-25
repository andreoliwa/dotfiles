# Remove python compiled byte-code in either current directory or in a
# list of specified directories
def _pyclean(args):
    places = '.' if not args else ' '.join(args)
    evalx(f"find {places} -type f -name '*.py[co]' -delete")
    evalx(f"find {places} -type d -name '__pycache__' -delete")
aliases["pyclean"] = _pyclean

# Clear all ipdb statements
def _rmpdb(args):
    git ls-files -oc --exclude-standard "*.py" | cat | xargs sed -i '' '/import ipdb;/d'
    echo "Cleared breakpoints"
aliases["rmpdb"] = _rmpdb
