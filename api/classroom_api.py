from flask import Blueprint, request, jsonify
from __init__ import db
from model.classroom import Classroom
from model.user import User

classroom_api = Blueprint('classroom_api', __name__, url_prefix='/api/classrooms')

def get_all_classrooms():
    classrooms = Classroom.query.all()
    return jsonify([c.to_dict() for c in classrooms])

def get_classroom_by_id(id):
    classroom = Classroom.query.get_or_404(id)
    return jsonify(classroom.to_dict())

def create_new_classroom():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return {"message": "Classroom name is required"}, 400

    classroom = Classroom(name=name)
    classroom.create()
    return jsonify(classroom.to_dict()), 201

def delete_classroom_by_id(id):
    classroom = Classroom.query.get_or_404(id)
    db.session.delete(classroom)
    db.session.commit()
    return {"message": "Classroom deleted"}, 200

def list_students_in_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    # Use dict representation if possible, else fallback
    students = []
    for s in classroom.students:
        try:
            students.append(s.to_dict())
        except AttributeError:
            students.append({"id": s.id, "name": getattr(s, "name", None)})
    return jsonify(students)

def get_student_in_classroom(id, student_id):
    classroom = Classroom.query.get_or_404(id)
    student = User.query.get_or_404(student_id)
    if not classroom.students.filter_by(id=student.id).first():
        return {"message": "Student not in this classroom"}, 404
    try:
        return jsonify(student.to_dict())
    except AttributeError:
        return jsonify({"id": student.id, "name": getattr(student, "name", None)})

def add_student_to_classroom(id, student_id):
    classroom = Classroom.query.get_or_404(id)
    student = User.query.get_or_404(student_id)

    if classroom.students.filter_by(id=student.id).first():
        return {"message": "Student already in classroom"}, 400

    classroom.students.append(student)
    db.session.commit()
    # Use _name or fallback to id if username not available
    student_name = getattr(student, "username", None) or getattr(student, "_name", None) or f"ID {student.id}"
    classroom_name = getattr(classroom, "name", f"ID {classroom.id}")
    return {"message": f"Student {student_name} added to classroom {classroom_name}"}, 201

def remove_student_from_classroom(id, student_id):
    classroom = Classroom.query.get_or_404(id)
    student = User.query.get_or_404(student_id)

    if not classroom.students.filter_by(id=student.id).first():
        return {"message": "Student not in this classroom"}, 404

    classroom.students.remove(student)
    db.session.commit()
    student_name = getattr(student, "username", None) or getattr(student, "_name", None) or f"ID {student.id}"
    classroom_name = getattr(classroom, "name", f"ID {classroom.id}")
    return {"message": f"Student {student_name} removed from classroom {classroom_name}"}, 200

def update_classroom(id):
    classroom = Classroom.query.get_or_404(id)
    data = request.get_json()
    name = data.get('name')
    if name:
        classroom.name = name
        db.session.commit()
        return jsonify(classroom.to_dict())
    return {"message": "No valid fields to update"}, 400



# ROUTES

classroom_api.route('/', methods=['GET'])(get_all_classrooms)
classroom_api.route('/<int:id>', methods=['GET'])(get_classroom_by_id)
classroom_api.route('/', methods=['POST'])(create_new_classroom)
classroom_api.route('/<int:id>', methods=['DELETE'])(delete_classroom_by_id)
classroom_api.route('/<int:id>', methods=['PUT'])(update_classroom)

classroom_api.route('/<int:id>/students', methods=['GET'])(list_students_in_classroom)
classroom_api.route('/<int:id>/students/<int:student_id>', methods=['GET'])(get_student_in_classroom)
classroom_api.route('/<int:id>/students/<int:student_id>', methods=['POST'])(add_student_to_classroom)
classroom_api.route('/<int:id>/students/<int:student_id>', methods=['DELETE'])(remove_student_from_classroom)
