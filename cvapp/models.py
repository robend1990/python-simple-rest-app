from cvapp import db


class UserSkillAssociation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    skill = db.relationship('Skill')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    cv_url = db.Column(db.String(255), nullable=True)
    skillAssociations = db.relationship('UserSkillAssociation', lazy=True, cascade="all, delete-orphan")


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)