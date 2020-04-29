virtualenv_path=.venv

develop:
	python3 -m venv $(virtualenv_path)
	./${virtualenv_path}/bin/pip install -r requirements.txt