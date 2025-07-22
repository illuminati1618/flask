from datetime import datetime

class Classroom:
    def __init__(self, id, name, schoolName, ownerTeacherId, status='active', createdAt=None):
        self.id = id
        self.name = name
        self.schoolName = schoolName
        self.ownerTeacherId = ownerTeacherId
        self.status = status
        self.createdAt = createdAt or datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'schoolName': self.schoolName,
            'ownerTeacherId': self.ownerTeacherId,
            'status': self.status,
            'createdAt': self.createdAt.isoformat()
        }

class User:
    def __init__(self, id, name, role, schoolName, status='active'):
        self.id = id
        self.name = name
        self.role = role  # 'teacher' or 'student' or 'admin'
        self.schoolName = schoolName
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'schoolName': self.schoolName,
            'status': self.status
        }

# Association table for many-to-many relationship between students and classrooms
class StudentClassroom:
    def __init__(self, student_id, classroom_id):
        self.student_id = student_id
        self.classroom_id = classroom_id

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'classroom_id': self.classroom_id
        }
