from cvapp import ma
from marshmallow import fields, post_load
from cvapp.models import DbUser

_skill_min_level = 1
_skill_max_level = 5
_skill_validation_error = f'Invalid value. Skills needs to have string name and an integer level ' \
    f'in range from {_skill_min_level} to {_skill_max_level}. For example: "python": 5'


class UserSchema(ma.SQLAlchemySchema):

    @staticmethod
    def get_skills_dict(user: DbUser):
        return {association.skill.name: association.level for association in user.skill_associations}

    @staticmethod
    def validate_skills(skills):
        for skill_name, skill_level in skills.items():
            return isinstance(skill_name, str) and isinstance(skill_level, int) and _skill_min_level <= skill_level <= _skill_max_level

    class Meta:
        model = DbUser

    id = ma.auto_field()
    last_name = ma.auto_field()
    first_name = ma.auto_field()
    cv_url = fields.Url()
    skills = fields.Function(get_skills_dict.__func__,
                             deserialize=lambda skills: skills,
                             validate=validate_skills.__func__,
                             error_messages={'validator_failed': _skill_validation_error})

    @post_load
    def make_db_user_with_skills_to_associate(self, data, **kwargs):
        skills_to_associate = data.get('skills', {})
        return DbUser(first_name=data['first_name'],
                      last_name=data['last_name'],
                      cv_url=data.get('cv_url'),
                      skill_associations=[]), skills_to_associate


users_schema = UserSchema(many=True)
user_schema = UserSchema()
