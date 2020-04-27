from cvapp import app
from flask import jsonify, make_response
from flask import abort
from cvapp.models import User
from cvapp.schemas import users_schema, user_schema
from cvapp import db


@app.route('/users', methods=['GET'])
def get_all_users():
    return jsonify(users_schema.dump(User.query.all())), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return abort(404, description=f'User with id {user_id} was not found')
    return jsonify(user_schema.dump(user)), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return abort(404, description=f'User with id {user_id} was not found')
    db.session.delete(user)
    db.session.commit()
    return make_response('', 204)

#TODO: create_user endpoint


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'description': error.description}), 404)
