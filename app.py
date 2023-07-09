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
    """
    This function takes a file as input in the request header
    and then uses openAI apis to extract required information
    from it. It then returns the extracted variables in the
    'data' attribute in a dictionary.
    """
    file_path = ''

    try:
        app.logger.info("Reading file in process_text")
        file = request.files['file']
        # Retrieve the logging level from the request object
        log_level = request.headers.get('X-Log-Level', 'NOTSET')
        console_log_level = getattr(logging, log_level.upper(), None) if log_level else None

        if file:
            time_string = time.strftime("%Y%m%d-%H%M%S")
            app.logger.info(f"writing {file} to file/{time_string}.pdf")
            # print(f"file/{time_string}.pdf")
            file_path = f"file/{time_string}.pdf"
            file.save(file_path)
            result = asyncio.run(extract_content(file_path, console_log_level, app.logger))
            os.remove(file_path)
            return result

    except Exception as e:
        # delete the file
        os.remove(file_path)
        # log an error message
        error_msg_with_traceback = f"An error occurred while processing the request: {str(e)}\n\n{traceback.format_exc()}"
        app.logger.error(error_msg_with_traceback)
        return jsonify(error=error_msg_with_traceback), 500


@app.route('/api/v1/generate-corrections-prompt', methods=['POST'])
@token_required
def process_corrections():
    try:
        app.logger.info("Getting corrections and result dictionaries from the request body")
        data = request.get_json()

        app.logger.info("Checking if corrections and result are present")
        corrections = data.get('corrections')
        result = data.get('result')

        if corrections is None or result is None:
            return jsonify(error='Invalid request. Corrections and result are required.'), 400

        app.logger.info("Checking if corrections and result are dictionaries")
        if not isinstance(corrections, dict) or not isinstance(result, dict):
            return jsonify(error='Corrections and result should be dictionaries.'), 400

        app.logger.info("Checking if result dictionary has necessary attributes")
        required_attributes = ['env_vars', 'config', 'cleaned_text']
        missing_attributes = []
        for attr in required_attributes:
            if attr not in result:
                missing_attributes.append(f"Missing attribute '{attr}' in result dictionary.")
        if missing_attributes:
            return jsonify(error=missing_attributes), 400

        app.logger.info("Calling the generate_correction_prompt function")
        prompt = generate_correction_prompt(corrections, result)

        # Return the prompt as a JSON response
        return jsonify(prompt=prompt)

    except Exception as e:
        error_msg_with_traceback = f"An error occurred: {str(e)}\n\n{traceback.format_exc()}"
        return jsonify(error=error_msg_with_traceback), 500


if __name__ == '__main__':
    app.run(debug=True)
