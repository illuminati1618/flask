
"""
Gemini API for handling requests to the Gemini language model.
Supports text analysis, citation checking, and other AI-powered features.

Example frontend JavaScript code for reference:
const API_KEY = "your-api-key-here";
const ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEY}`;
fetch(ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        contents: [{
            parts: [{ text: `Please look at this text for correct academic citations, and recommend APA references for each area of concern: ${text}` }]
        }]
    })
});
"""
    
from flask import Blueprint, request, jsonify, current_app, g
from flask_restful import Api, Resource
import requests
from api.jwt_authorize import token_required

gemini_api = Blueprint('gemini_api', __name__, url_prefix='/api')
api = Api(gemini_api)

class GeminiAPI:
    class _Ask(Resource):
        """
        Gemini API Resource to handle requests to the Gemini language model.
        Supports various AI-powered text analysis tasks.
        """
        @token_required()
        def post(self):
            """
            Send a request to the Gemini API.
            
            Expected JSON body:
            {
                "text": "Text to analyze",
                "prompt": "Optional custom prompt" (defaults to citation analysis)
            }
            
            Returns:
                JSON response from Gemini API or error message
            """
            current_user = g.current_user
            body = request.get_json()
            
            # Validate request body
            if not body:
                return {'message': 'Request body is required'}, 400
            
            text = body.get('text', '')
            if not text:
                return {'message': 'Text field is required'}, 400
            
            # Get configuration
            api_key = current_app.config.get('GEMINI_API_KEY')
            server = current_app.config.get('GEMINI_SERVER')
            
            if not api_key:
                return {'message': 'Gemini API key not configured'}, 500
            
            if not server:
                return {'message': 'Gemini server not configured'}, 500
            
            # Build the endpoint URL
            endpoint = f"{server}?key={api_key}"
            
            # Default prompt for citation analysis, can be overridden
            default_prompt = f"Please look at this text for correct academic citations, and recommend APA references for each area of concern: {text}"
            prompt = body.get('prompt', default_prompt)
            
            # Prepare the request payload for Gemini API
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            # Log the request for auditing purposes
            current_app.logger.info(f"User {current_user.uid} made a Gemini API request")
            
            try:
                # Make request to Gemini API
                response = requests.post(
                    endpoint,
                    headers={'Content-Type': 'application/json'},
                    json=payload,
                    timeout=30  # 30 second timeout
                )
                
                # Check if the request was successful
                if response.status_code != 200:
                    current_app.logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
                    return {'message': f'Gemini API error: {response.status_code}'}, 500
                
                # Parse the response
                result = response.json()
                
                # Extract the generated text
                try:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    return {
                        'success': True,
                        'text': generated_text,
                        'user': current_user.uid
                    }
                except (KeyError, IndexError) as e:
                    current_app.logger.error(f"Error parsing Gemini response: {e}")
                    return {
                        'success': False,
                        'message': 'Error parsing Gemini API response',
                        'raw_response': result
                    }, 500
                    
            except requests.RequestException as e:
                current_app.logger.error(f"Error communicating with Gemini API: {e}")
                return {'message': f'Error communicating with Gemini API: {str(e)}'}, 500
            except Exception as e:
                current_app.logger.error(f"Unexpected error in Gemini API: {e}")
                return {'message': f'Unexpected error: {str(e)}'}, 500

    class _Health(Resource):
        """
        Health check endpoint for Gemini API integration.
        """
        @token_required()
        def get(self):
            """
            Check if Gemini API is properly configured.
            
            Returns:
                JSON response indicating configuration status
            """
            api_key = current_app.config.get('GEMINI_API_KEY')
            server = current_app.config.get('GEMINI_SERVER')
            
            return {
                'gemini_configured': bool(api_key and server),
                'server': server if server else 'Not configured',
                'api_key_present': bool(api_key)
            }

    # Register endpoints
    api.add_resource(_Ask, '/gemini')
    api.add_resource(_Health, '/gemini/health')