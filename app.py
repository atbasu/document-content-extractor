from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import JWTManager
from functools import wraps
from document_content_extractor import *
import time
import jwt
import asyncio
import nest_asyncio
nest_asyncio.apply()
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'closewise-secret'

# Decorators
def token_required(f):
   @wraps(f)
   def decorated(*args, **kwargs):
       
       token = None
       if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split()[1]
       if not token:
            return jsonify({'message': 'Token is missing!'}), 401
       try:
          data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
          request.token_data = data
       except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
       except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401     
       return f(*args, **kwargs)
   return decorated

async def extract_content(filePath):
   return run_app(filePath)

# Routeslk
@app.route('/api/v1/multipart-parse', methods=['POST'])
@token_required
def process_text():
    file_path = ''
    try:
       file = request.files['file']
       if file:
              timeString = time.strftime("%Y%m%d-%H%M%S")
              print(f"file/{timeString}.pdf")
              filePath = f"file/{timeString}.pdf"
              file.save(filePath)
              run_id, run_time, file_path, api_key, usage, model, json_result = asyncio.run(extract_content(filePath))
              os.remove(filePath)
              return json_result

    except Exception as e:
       app.logger.error(str(e))
       errorMessage = "An error occurred while processing the request"
       os.remove(filePath)
       return jsonify({ 'error': errorMessage }), 500

if __name__ == '__main__':
    app.debug = True
    http_server = WSGIServer(('', 4500), app)
    http_server.serve_forever()
