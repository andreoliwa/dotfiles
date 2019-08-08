# Remove python compiled byte-code in either current directory or in a
# list of specified directories
function pyclean() {
    find . -type f -name '*.py[co]' -delete
    find . -type d -name '__pycache__' -delete
}

# Clear all ipdb statements
functionrmpdb() {
    git ls-files -oc --exclude-standard "*.py" | cat | xargs sed -i '' '/import ipdb;/d'
    echo "Cleared breakpoints"
}
