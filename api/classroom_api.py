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

