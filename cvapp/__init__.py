import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


db_user = os.environ["MYSQL_USER"]
db_password = os.environ["MYSQL_PASSWORD"]
db_server = os.getenv("MYSQL_SERVER", "localhost:3306")
db_name = os.environ["MYSQL_DATABASE"]
s3_bucket_name = os.environ["S3_BUCKET"]

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_server}/{db_name}?charset=utf8mb4'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
ma = Marshmallow(app)

from cvapp import routes
