# Requirements

- Python 3.7 or greater
- virtualenv
- Properly configured `default` profile in `~/.aws/credentials` with access to read/write S3 resources
- docker
- make 

# Developer guide

To start working on any changes: 
- cd to root path of the project
- run `make develop` to create virtualv with all dependencies installed in it.
Then select `[working_dir].venv/bin/python3.7` as interpreter in your IDE.
- activate virtualenv with `source .venv/bin/activate`
- adjust env vars in `dev_envs` to fit into your environment
- run mysql container with `docker run --name mysql-container --env-file dev_envs -d -p 3306:3306  mysql`'
- export envs from `dev_envs` to your shell. Set them also in Run/Debug configuration of your IDE if you want to run app from there
- to run migration script(s), execute: `PYTHONPATH=. alembic upgrade head`
- to start the app run `python run.py`

# What does this app do?

The app is a simple REST app which exposes few endpoints that allow to save/remove users with some additional data about them.
For example what skills they have and from what URL you can download their's CV document:

- /users [POST]  
Saves user and his skills in the database. Downloads CV from given url (if provided) and copies it to the S3 bucket.
Responds with status code 201 if succeeded.
Example request body:

```json
{
    "first_name": "John",
    "last_name": "Doe",
    "cv_url": "https://url_to_download_cv",
    "skills": {
        "python": 5,
        "java": 3,
        "ruby": 1 
    }
}
```

- /users [GET]  
Returns list with information about all users in db.
If CV file for user exists then cv_url property in the response is replaced with presigned url to CV that is stored on S3.
Responds with status code 200 if succeeded.
Example response:

```json
[
  {
    "cv_url": "https://[presigned_url_to_cv]",
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "skills": {
      "java": 3,
      "js": 5,
      "ruby": 1
    }
  }
]
```

- /users/<int:user_id> [GET]  
Returns json object with information about one particular user - with id that is given in `user_id` path param.
If CV file for user exists, then cv_url property in the response is replaced with presigned url to CV that is stored on S3.
Responds with status code 200 if succeeded.

- /users/<int:user_id> [DELETE]
Removes user with given id. If CV for user exists in S3, then object is also removed.
If any skills associations for user exist, then they are removed as well.
Responds with status code 204 if succeeded.
