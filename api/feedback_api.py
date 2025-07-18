import os
import requests
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from model.feedback import Feedback
from __init__ import app, db

feedback_api = Blueprint('feedback_api', __name__, url_prefix='/api/feedback')
api = Api(feedback_api)

GITHUB_REPO = "blackstar3092/ocs_data_and_com_pages"  
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

class FeedbackAPI:
    class _Create(Resource):
        def post(self):
            data = request.get_json()
            title = data.get('title')
            body = data.get('body')

            if not title or not body:
                return {"message": "Title and body are required."}, 400

            feedback = Feedback(title, body).create()

            # Attempt to create GitHub issue
            headers = {
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json"
            }
            payload = {
                "title": f"[User Feedback] {title}",
                "body": body,
                "labels": ["feedback"]
            }

            try:
                response = requests.post(
                    f"https://api.github.com/repos/blackstar3092/ocs_data_and_com_pages/issues",
                    headers=headers,
                    json=payload
                )
                if response.status_code == 201:
                    github_url = response.json()["html_url"]
                    feedback.github_issue_url = github_url
                    db.session.commit()
                else:
                    print("GitHub Issue creation failed:", response.json())
            except Exception as e:
                print("GitHub API error:", str(e))

            return jsonify(feedback.read())

    class _ReadAll(Resource):
        def get(self):
            feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
            return jsonify([f.read() for f in feedbacks])

api.add_resource(FeedbackAPI._Create, '/')
api.add_resource(FeedbackAPI._ReadAll, '/all')
