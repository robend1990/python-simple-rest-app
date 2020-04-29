from cvapp import ma
from marshmallow import fields
from cvapp.models import DbUser


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DbUser

    id = ma.auto_field()
    last_name = ma.auto_field()
    first_name = ma.auto_field()
    cv_url = ma.auto_field()
    skills = fields.Method("get_skills_dict")

    def get_skills_dict(self, user):
        return {association.skill.name: association.level for association in user.skill_associations}


users_schema = UserSchema(many=True)
user_schema = UserSchema()