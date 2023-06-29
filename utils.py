import argparse
import configparser
import json
import logging
import os
import time

import PyPDF2
from pdfminer.high_level import extract_text


def get_formatted_prompt_fields(config, filter_func):
    return [f'{field}: {properties["description"]}' for field, properties in config.items() if
            filter_func(field, properties)]


def format_prompt(prefix, fields_list, midfix, cleaned_text, suffix):
    return f"{prefix}\n" + '\n'.join(fields_list) + f"\n{midfix}\n{cleaned_text}\n{suffix}"


def setup_logging(run_id, console_level=logging.NOTSET):
    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(console_level)

    # Create the logs directory if it doesn't exist
    env_vars = read_env_vars(["results_folder"])
    logs_dir = f'./{env_vars["results_folder"]}/logs'
    os.makedirs(logs_dir, exist_ok=True)

    # Create a file handler that writes log messages to a file
    timestamp = time.strftime('%Y%m%d%H%M%S')
    log_file = os.path.join(logs_dir, f"DCE_{run_id}_{timestamp}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    """
    # Create a console handler if the console level is specified
    if console_level != logging.NOTSET and console_level != logging.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    """

    return logger


def read_document_PYPDF2(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text


def read_document(file_path):
    text = extract_text(file_path)
    return text


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def read_args(api_key, model, parser_config, splits):
    # read user provided arguments
    parser = argparse.ArgumentParser(description='Extract and process content from a document')
    parser.add_argument('--file', help='path to document file', default=None)
    parser.add_argument('--api-key', help='OpenAI API key', default=api_key)
    parser.add_argument(
        '--model',
        help='OpenAI model name see https://platform.openai.com/docs/models/overview',
        default=model)
    parser.add_argument(
        '--parser-config',
        help='path to json file containing parser configuration',
        default=parser_config)
    parser.add_argument(
        '--splits',
        help='number of splits to divide prompt into',
        default=splits)
    parser.add_argument(
        '--log-level',
        help='logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)',
        default='NOTSET')

    args = parser.parse_args()

    # Convert log level to a valid logging level
    log_level = getattr(logging, args.log_level.upper(), logging.NOTSET)
    print(f"Using logging level {log_level}")
    args.log_level = log_level

    return args


def read_env_vars(variables: object = None) -> dict:
    config = configparser.ConfigParser()
    config.read('config.ini')

    variables_dict = {
        option: int(value) if value.isdigit() else value
        for section in config.sections()
        for option, value in config.items(section)
        if variables is None or option in variables
    }

    return variables_dict


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def write_result_to_json(dictionary, file_name, folder_name):
    # Create directory if it doesn't exist
    if dictionary:
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        # Create full file path for results
        result_file_path = f'{folder_name}/{file_name}'

        # Write result to JSON file
        with open(result_file_path, 'w') as f:
            json.dump(dictionary, f, cls=CustomEncoder)
    else:
        result_file_path = "no data for this file"

    return result_file_path


def read_stopwords(file_path):
    with open(file_path, 'r') as file:
        stopwords = {line.strip() for line in file if line.strip()}
    return stopwords
