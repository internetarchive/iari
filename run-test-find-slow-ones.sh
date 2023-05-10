# This change of directory is needed for the test to find the test_data directory
cd tests/
poetry run python -m pytest --durations=10
