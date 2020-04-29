from cvapp import db


class DbUserSkillAssociation(db.Model):
    __tablename__ = 'user_skill_association'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skill.id'), primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    skill = db.relationship('DbSkill')


class DbUser(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    cv_url = db.Column(db.String(255), nullable=True)
    skill_associations = db.relationship('DbUserSkillAssociation', lazy=True, cascade="all, delete-orphan")


class DbSkill(db.Model):
    __tablename__ = 'skill'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
