rm dist/*
python setup.py sdist bdist_wheel

python -m twine check dist/*

python -m twine upload --config-file=~/.pypirc dist/*