virtualenv_path=.venv

develop:
	virtualenv -p python3.7 $(virtualenv_path)
	./${virtualenv_path}/bin/pip install -r requirements.txt