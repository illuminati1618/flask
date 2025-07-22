from flask import Blueprint, request, jsonify
from model.classroom import Classroom, User
from datetime import datetime
import uuid

classrooms_db = {}
users_db = {}

classroom_api = Blueprint('classroom_api', __name__)

def get_current_user():
    # Placeholder: Replace with real authentication
    user_id = request.headers.get('X-User-Id')
    return users_db.get(user_id)

@classroom_api.route('/api/classrooms', methods=['GET'])
def list_classrooms():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    if user.role == 'admin':
        return jsonify([c.to_dict() for c in classrooms_db.values()])
    return jsonify([
        c.to_dict() for c in classrooms_db.values()
        if c.schoolName == user.schoolName
    ])

@classroom_api.route('/api/classrooms', methods=['POST'])
def create_classroom():
    user = get_current_user()
    if not user or user.role not in ['teacher', 'admin']:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    classroom_id = str(uuid.uuid4())
    classroom = Classroom(
        id=classroom_id,
        name=data['name'],
        schoolName=user.schoolName if user.role == 'teacher' else data.get('schoolName'),
        ownerTeacherId=user.id if user.role == 'teacher' else data.get('ownerTeacherId'),
        status='active',
        createdAt=datetime.utcnow()
    )
    classrooms_db[classroom_id] = classroom
    return jsonify(classroom.to_dict()), 201

@classroom_api.route('/api/classrooms/<classroom_id>', methods=['GET'])
def get_classroom(classroom_id):
    user = get_current_user()
    classroom = classrooms_db.get(classroom_id)
    if not classroom:
        return jsonify({'error': 'Not found'}), 404
    if user.role == 'admin' or (user.role == 'teacher' and classroom.ownerTeacherId == user.id):
        return jsonify(classroom.to_dict())
    if classroom.schoolName == user.schoolName:
        return jsonify(classroom.to_dict())
    return jsonify({'error': 'Forbidden'}), 403

@classroom_api.route('/api/classrooms/<classroom_id>', methods=['PUT'])
def update_classroom(classroom_id):
    user = get_current_user()
    classroom = classrooms_db.get(classroom_id)
    if not classroom:
        return jsonify({'error': 'Not found'}), 404
    if user.role not in ['admin', 'teacher'] or (user.role == 'teacher' and classroom.ownerTeacherId != user.id):
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    classroom.name = data.get('name', classroom.name)
    classroom.status = data.get('status', classroom.status)
    classrooms_db[classroom_id] = classroom
    return jsonify(classroom.to_dict())

@classroom_api.route('/api/classrooms/<classroom_id>', methods=['DELETE'])
def delete_classroom(classroom_id):
    user = get_current_user()
    classroom = classrooms_db.get(classroom_id)
    if not classroom:
        return jsonify({'error': 'Not found'}), 404
    if user.role not in ['admin', 'teacher'] or (user.role == 'teacher' and classroom.ownerTeacherId != user.id):
        return jsonify({'error': 'Forbidden'}), 403
    classroom.status = 'archived'
    return jsonify({'message': 'Classroom archived'})

@classroom_api.route('/api/classrooms/<classroom_id>/enroll', methods=['POST'])
def enroll_student(classroom_id):
    user = get_current_user()
    classroom = classrooms_db.get(classroom_id)
    if not classroom or user.role != 'student':
        return jsonify({'error': 'Forbidden'}), 403
    if classroom.schoolName != user.schoolName:
        return jsonify({'error': 'School mismatch'}), 403
    if classroom_id not in user.classrooms:
        user.classrooms.append(classroom_id)
    return jsonify({'message': 'Enrolled'})

@classroom_api.route('/api/classrooms/<classroom_id>/students', methods=['GET'])
def get_classroom_students(classroom_id):
    user = get_current_user()
    classroom = classrooms_db.get(classroom_id)
    if not classroom:
        return jsonify({'error': 'Not found'}), 404
    if user.role not in ['admin', 'teacher'] or (user.role == 'teacher' and classroom.ownerTeacherId != user.id):
        return jsonify({'error': 'Forbidden'}), 403
    students = [u.to_dict() for u in users_db.values() if u.role == 'student' and classroom_id in u.classrooms]
    return jsonify(students)

@classroom_api.route('/api/classrooms/<classroom_id>/students', methods=['POST'])
def add_student_to_classroom(classroom_id):
    user = get_current_user()
    classroom = classrooms_db.get(classroom_id)
    if not classroom:
        return jsonify({'error': 'Not found'}), 404
    if user.role not in ['admin', 'teacher'] or (user.role == 'teacher' and classroom.ownerTeacherId != user.id):
        return jsonify({'error': 'Forbidden'}), 403
    data = request.json
    student_id = data['studentId']
    student = users_db.get(student_id)
    if not student or student.role != 'student' or student.schoolName != classroom.schoolName:
        return jsonify({'error': 'Invalid student'}), 400
    if classroom_id not in student.classrooms:
        student.classrooms.append(classroom_id)
    return jsonify({'message': 'Student added'})

@classroom_api.route('/api/classrooms/<classroom_id>/students/<student_id>', methods=['DELETE'])
def remove_student_from_classroom(classroom_id, student_id):
    user = get_current_user()
    classroom = classrooms_db.get(classroom_id)
    student = users_db.get(student_id)
    if not classroom or not student:
        return jsonify({'error': 'Not found'}), 404
    if user.role not in ['admin', 'teacher'] or (user.role == 'teacher' and classroom.ownerTeacherId != user.id):
        return jsonify({'error': 'Forbidden'}), 403
    if classroom_id in student.classrooms:
        student.classrooms.remove(classroom_id)
    return jsonify({'message': 'Student removed'})


