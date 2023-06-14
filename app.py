import asyncio
from functools import wraps

import jwt
import nest_asyncio
from flask import Flask, jsonify, request

from document_content_extractor import *

nest_asyncio.apply()

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


async def extract_content(file_path):
    return run_app(file_path)


# Routes
@app.route('/api/v1/multipart-parse', methods=['POST'])
@token_required
def process_text():
    file_path = ''
    try:
        file = request.files['file']
        if file:
            time_string = time.strftime("%Y%m%d-%H%M%S")
            print(f"file/{time_string}.pdf")
            file_path = f"file/{time_string}.pdf"
            file.save(file_path)
            result = asyncio.run(extract_content(file_path))
            os.remove(file_path)
            return result

    except Exception as e:
        app.logger.error(str(e))
        error_message = "An error occurred while processing the request"
        os.remove(file_path)
        return jsonify({'error': error_message}), 500


if __name__ == '__main__':
    app.run(debug=True)
