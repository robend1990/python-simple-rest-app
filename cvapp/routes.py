import tempfile

from marshmallow import ValidationError
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import InternalServerError

from cvapp import app
from flask import jsonify, request
from flask import abort
from cvapp.models import DbUser, DbUserSkillAssociation, DbSkill
from cvapp.schemas import users_schema, user_schema
from cvapp import db, s3_bucket_name
import requests
import boto3


@app.route('/user', methods=['GET'])
def get_all_users():
    users = db.session.query(DbUser).options(joinedload(DbUser.skill_associations)
                                             .subqueryload(DbUserSkillAssociation.skill)
                                             ).all()
    return jsonify(users_schema.dump(users)), 200


@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = DbUser.query.get(user_id)
    if user is None:
        return abort(404, description=f'User with id {user_id} was not found')
    return jsonify(user_schema.dump(user)), 200


@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = DbUser.query.get(user_id)
    if user is None:
        return abort(404, description=f'User with id {user_id} was not found')
    db.session.delete(user)
    db.session.commit()
    return '', 204


@app.route('/user', methods=['POST'])
def create_user_with_associations():
    user, skills_to_associate = user_schema.load(request.get_json())
    presigned_url = copy_file_from_url_to_s3(user)
    user.cv_url = presigned_url
    create_missing_skills(skills_to_associate)
    associate_user_with_skills(user, skills_to_associate)
    db.session.add(user)
    db.session.commit()
    return '', 201


@app.errorhandler(404)
def not_found(error):
    return jsonify({'description': error.description}), 404


@app.errorhandler(ValidationError)
def invalid_request_body(error):
    return jsonify({'description': error.messages}), 400


def copy_file_from_url_to_s3(user):
    with tempfile.NamedTemporaryFile() as tf:
        downloaded_cv = requests.get(user.cv_url)
        tf.write(downloaded_cv.content)
        s3 = boto3.client('s3')
        key = f'{user.last_name}/{user.first_name}/cv'
        s3.upload_file(tf.name, s3_bucket_name, key)
        url = s3.generate_presigned_url(ClientMethod='get_object',
                                  Params={'Bucket': s3_bucket_name, 'Key': key},
                                  ExpiresIn=300)
    return url


def create_missing_skills(skills_to_associate):
    skills = []
    for skill_name in skills_to_associate.keys():
        if DbSkill.query.filter_by(name=skill_name).first() is None:
            skill = DbSkill(name=skill_name)
            skills.append(skill)
            db.session.add(skill)
    return skills


def associate_user_with_skills(user, skills_to_associate):
    for skill_name, skill_level in skills_to_associate.items():
        skill = DbSkill.query.filter_by(name=skill_name).first()
        if skill is None:
            raise InternalServerError(description=f"Skill {skill_name} was not found in DB")
        user_skill_association = DbUserSkillAssociation(skill=skill, level=skill_level)
        user.skill_associations.append(user_skill_association)

# TODO: Add removal of the file from s3 inside delete_user
# TODO: move some business logic to its own module and add some exception handling