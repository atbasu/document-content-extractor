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


async def extract_content(file_path, console_log_level, app_logger=None):
    return run_app(file_path, console_log_level, app_logger)


# Routes
@app.route('/api/v1/ai-parse', methods=['POST'])
@token_required
def process_text():
    file_path = ''

    try:
        app.logger.info("Reading file in process_text")
        file = request.files['file']
        # Retrieve the logging level from the request object
        log_level = request.headers.get('X-Log-Level')
        console_log_level = getattr(logging, log_level.upper(), None) if log_level else None

        if file:
            time_string = time.strftime("%Y%m%d-%H%M%S")
            app.logger.info(f"writing {file} to file/{time_string}.pdf")
            app.logger.info(f"writing {file} to file/{time_string}.pdf")
            # print(f"file/{time_string}.pdf")
            file_path = f"file/{time_string}.pdf"
            file.save(file_path)
            result = asyncio.run(extract_content(file_path, console_log_level, app.logger))
            os.remove(file_path)
            return result

    except Exception as e:
        app.logger.error(str(e))
        error_message = "An error occurred while processing the request"
        os.remove(file_path)
        return jsonify({'error': error_message}), 500


@app.route('/api/v1/closewise-format', methods=['POST'])
@token_required
def format_for_closewise(data):
    try:
        data = request.headers.get('data', {})
        data = dict(data)
    except Exception as e:
        return jsonify({'error': 'Invalid data format'}), 400

    output = {
        "borrowers": [],
        "propertyAddress": {},
        "closingAddress": {}
    }

    try:
        for key, value in data.items():
            if value:
                if "Address_" in key:
                    address_type, address_field = key.split("_")[0], key.split("_")[1]
                    output[address_type][address_field] = value
                elif "borrower" in key:
                    attribute, num = key.split("_")
                    # Adjust index to 0-based
                    index = int(num) - 1
                    # added empty list elements till the length of list matches the current index
                    while index >= len(output["borrowers"]):
                        output["borrowers"].append({})
                    borrower_info = output["borrowers"][index]
                    borrower_info[attribute] = value
                else:
                    output[key] = value
    except Exception as e:
        return jsonify({'error': 'Error processing data'}), 500

    return jsonify(output)


if __name__ == '__main__':
    app.run(debug=True)
