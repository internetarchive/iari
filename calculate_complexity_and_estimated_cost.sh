# https://aur.archlinux.org/packages/scc-bin <- the software used here
echo src/models:
scc src/models
echo src/helpers:
scc src/helpers
echo tests:
scc tests
#echo "all python files:"
#scc *.py
echo "Total:"
scc \
--exclude-dir .mypy_cache \
--exclude-dir .pytest_cache \
--exclude-dir lib \
--exclude-dir venv \
 -M ".*\\.csv"
