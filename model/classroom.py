from datetime import datetime
from sqlalchemy.exc import IntegrityError
from __init__ import db  # Your SQLAlchemy db instance

class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), nullable=False)
    _school_name = db.Column(db.String(255), nullable=False)
    _owner_teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _status = db.Column(db.String(50), default='active')
    _created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, school_name, owner_teacher_id, status='active'):
        self._name = name
        self._school_name = school_name
        self._owner_teacher_id = owner_teacher_id
        self._status = status

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def school_name(self):
        return self._school_name

    @school_name.setter
    def school_name(self, val):
        self._school_name = val

    @property
    def owner_teacher_id(self):
        return self._owner_teacher_id

    @owner_teacher_id.setter
    def owner_teacher_id(self, val):
        self._owner_teacher_id = val

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, val):
        self._status = val

    @property
    def created_at(self):
        return self._created_at

    def __str__(self):
        return str(self.to_dict())

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'school_name': self.school_name,
            'owner_teacher_id': self.owner_teacher_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
# Only for dev setup — safe to remove after table is created
if __name__ == "__main__":
    from __init__ import app, db
    with app.app_context():
        Classroom.__table__.create(db.engine, checkfirst=True)
        print("✅ Classroom table created.")
