import io
from botocore.exceptions import ClientError
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import HTTPException

from cvapp import app
from flask import jsonify, request
from flask import abort
from cvapp.models import DbUser, DbUserSkillAssociation, DbSkill
from cvapp.schemas import users_schema, user_schema
from cvapp import db, s3_bucket_name
import requests
import boto3


class CustomInternalServerError(HTTPException):
    code = 500
    description = 'Internal Server Error'


@app.route('/users', methods=['GET'])
def get_all_users():
    users = db.session.query(DbUser).options(joinedload(DbUser.skill_associations)
                                             .subqueryload(DbUserSkillAssociation.skill)
                                             ).all()
    for user in users:
        set_presigned_url_as_cv_url(user)
    return jsonify(users_schema.dump(users)), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.query(DbUser).options(joinedload(DbUser.skill_associations)
                                            .subqueryload(DbUserSkillAssociation.skill)
                                            ).get(user_id)
    if user is None:
        return abort(404, description=f'User with id {user_id} was not found')
    set_presigned_url_as_cv_url(user)
    return jsonify(user_schema.dump(user)), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = DbUser.query.get(user_id)
    if user is None:
        return abort(404, description=f'User with id {user_id} was not found')
    remove_cv_from_s3(user)
    db.session.delete(user)
    db.session.commit()
    return '', 204


@app.route('/users', methods=['POST'])
def create_user_with_associations():
    user, skills_to_associate = user_schema.load(request.get_json())
    cv_s3_key = copy_file_from_url_to_s3(user)
    user.cv_url = cv_s3_key
    db_skills = create_missing_skills(skills_to_associate)
    associate_user_with_skills(user, db_skills, skills_to_associate)
    db.session.add(user)
    db.session.commit()
    return '', 201


@app.errorhandler(404)
def not_found(error):
    return jsonify({'description': error.description}), 404


@app.errorhandler(CustomInternalServerError)
def internal_error(error):
    return jsonify({'description': error.description}), error.code


@app.errorhandler(ValidationError)
def invalid_request_body(error):
    return jsonify({'description': error.messages}), 400


def copy_file_from_url_to_s3(user):
    try:
        response = requests.get(user.cv_url)
        if response.status_code != 200:
            raise CustomInternalServerError(
                description=f"Downloading cv from {user.cv_url} failed with status code: {response.status_code}")
        s3 = boto3.client('s3')
        key = f'{user.last_name}/{user.first_name}/cv'
        s3.upload_fileobj(io.BytesIO(response.content), s3_bucket_name, key)
    except ClientError as e:
        raise CustomInternalServerError(description=e['Error']['Message'])
    return key


def create_missing_skills(skills_to_associate):
    existing_skills = DbSkill.query.filter(DbSkill.name.in_(skills_to_associate.keys())).all()
    existing_skill_names = [skill.name for skill in existing_skills]
    for skill_name in skills_to_associate.keys():
        if skill_name not in existing_skill_names:
            skill = DbSkill(name=skill_name)
            existing_skills.append(skill)
            db.session.add(skill)
    return existing_skills


def associate_user_with_skills(user, db_skills, skills_to_associate):
    for skill in db_skills:
        user_skill_association = DbUserSkillAssociation(skill=skill, level=skills_to_associate[skill.name])
        user.skill_associations.append(user_skill_association)


def remove_cv_from_s3(user):
    s3 = boto3.client('s3')
    key = f'{user.last_name}/{user.first_name}/cv'
    try:
        # head will throw an error if object does not exist
        s3.head_object(Bucket=s3_bucket_name, Key=key)
        s3.delete_object(Bucket=s3_bucket_name, Key=key)
    except ClientError as e:
        if e.response["Error"]["Code"] == '404':
            # nothing to delete
            return
        raise CustomInternalServerError(description=e.response['Error']['Message'])


def set_presigned_url_as_cv_url(db_user):
    if db_user.cv_url:
        s3 = boto3.client('s3')
        presigned_url = s3.generate_presigned_url(ClientMethod='get_object',
                                                  Params={'Bucket': s3_bucket_name, 'Key': db_user.cv_url},
                                                  ExpiresIn=300)
        db_user.cv_url = presigned_url
