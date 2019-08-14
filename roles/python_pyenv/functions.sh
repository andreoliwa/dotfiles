# Remove python compiled byte-code in either current directory or in a
# list of specified directories
function pyclean() {
    find . -type f -name '*.py[co]' -delete
    find . -type d -name '__pycache__' -delete
}

# Clear distribution files
function pyclean_dist() {
    find . -type d \( -name '*.egg-info' -or -name 'pip-wheel-metadata' -or -name 'dist' \) -print0 | xargs -0 rm -rvf
}

# Clear all ipdb statements
function rmpdb() {
    git ls-files -oc --exclude-standard "*.py" | cat | xargs sed -i '' '/import ipdb;/d'
    echo "Cleared breakpoints"
}
