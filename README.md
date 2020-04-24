# Requirements

- Python 3.7 or greater
- virtualenv
- make 

# Developer guide

To start working on any changes: 
- run `make develop` to create virtualv with all dependencies installed in it.
Then select `[working_dir].venv/bin/python3.7` as interpreter in your IDE.
- run mysql container with `docker run --name mysql-container --env-file mysql_dev_envs -v [working_dir]/startup_sql:/docker-entrypoint-initdb.d -d -p 3306:3306  mysql`'
- export envs from `mysql_dev_envs` to your shell or set them in Run/Debug configuration of your IDE

