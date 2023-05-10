# This change of directory is needed for the test to find the test_data directory
poetry run python -m coverage run -m pytest
poetry run python -m coverage report > TEST_COVERAGE.txt
echo "TEST_COVERAGE file updated"
