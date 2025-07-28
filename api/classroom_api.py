from flask import Blueprint, request, jsonify, g
from flask_restful import Api, Resource
from datetime import datetime
from __init__ import db
from api.jwt_authorize import token_required
from model.classroom import Classroom
from model.user import User  # Import User model for validation

classroom_api = Blueprint('classroom_api', __name__, url_prefix='/api')
api = Api(classroom_api)

class ClassroomListAPI(Resource):
    @token_required()
    def get(self):
        current_user = g.current_user
        if current_user.role == "Admin":
            classrooms = Classroom.query.all()
        else:
            classrooms = Classroom.query.filter_by(school_name=current_user.school).all()
        return jsonify([c.to_dict() for c in classrooms])

    @token_required(["Teacher", "Admin"])
    def post(self):
        data = request.get_json()
        name = data.get("name")
        if not name:
            return {"message": "Classroom name is required"}, 400

        current_user = g.current_user
        if current_user.role == "Teacher":
            school_name = current_user.school
            owner_teacher_id = current_user.id
        else:  # Admin
            school_name = data.get("school_name")
            owner_teacher_id = data.get("owner_teacher_id")
            if not school_name or not owner_teacher_id:
                return {"message": "school_name and owner_teacher_id required for Admin"}, 400

            # Optional validation: ensure owner_teacher_id belongs to a teacher
            owner = User.query.get(owner_teacher_id)
            if not owner or owner.role != "Teacher":
                return {"message": "owner_teacher_id must belong to a teacher"}, 400

        classroom = Classroom(
            name=name,
            school_name=school_name,
            owner_teacher_id=owner_teacher_id,
            status="active"
            # created_at is automatically set in model, no need to pass here
        )
        classroom.create()
        return jsonify(classroom.to_dict()), 201

class ClassroomDetailAPI(Resource):
    @token_required()
    def get(self, id):
        classroom = Classroom.query.get(id)
        if not classroom:
            return {"message": "Classroom not found"}, 404

        current_user = g.current_user
        if current_user.role != "Admin" and classroom.school_name != current_user.school:
            return {"message": "Forbidden"}, 403

        return jsonify(classroom.to_dict())

    @token_required(["Teacher", "Admin", "User"])
    def put(self, id):
        print("Incoming Headers:", request.headers)
        classroom = Classroom.query.get(id)
        if not classroom:
            return {"message": "Classroom not found"}, 404

        current_user = g.current_user
        if current_user.role == "Teacher" and classroom.owner_teacher_id != current_user.id:
            return {"message": "Forbidden"}, 403

        data = request.get_json()
        classroom.update(**data)
        return jsonify(classroom.to_dict())

    @token_required(["Teacher", "Admin"])
    def delete(self, id):
        classroom = Classroom.query.get(id)
        if not classroom:
            return {"message": "Classroom not found"}, 404

        current_user = g.current_user
        if current_user.role == "Teacher" and classroom.owner_teacher_id != current_user.id:
            return {"message": "Forbidden"}, 403

        classroom.status = "archived"
        db.session.commit()
        return {"message": f"Classroom {classroom.name} archived"}, 200

class ClassroomStudentsAPI(Resource):
    @token_required()
    def get(self, id):
        # Placeholder for getting students in classroom id
        return {"message": f"Get students in classroom {id}"}

    @token_required(["Teacher", "Admin"])
    def post(self, id):
        # Placeholder for adding a student to classroom id
        return {"message": f"Add student to classroom {id}"}

    @token_required(["Teacher", "Admin"])
    def delete(self, id):
        # Placeholder for removing a student from classroom id
        return {"message": f"Remove student from classroom {id}"}

# Add resource routing
api.add_resource(ClassroomListAPI, "/classrooms")
api.add_resource(ClassroomDetailAPI, "/classrooms/<int:id>")
api.add_resource(ClassroomStudentsAPI, "/classrooms/<int:id>/students")
