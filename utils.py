import argparse
import configparser
import json
import os

import PyPDF2


def read_document(file_path):
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
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
    return parser.parse_args()


def read_env_vars(variables: object = None) -> object:
    config = configparser.ConfigParser()
    config.read('config.ini')

    variables_dict = {
        option: int(value) if value.isdigit() else value
        for section in config.sections()
        for option, value in config.items(section)
        if variables is None or option in variables
    }

    return variables_dict


def write_result_to_json(dictionary, file_name, folder_name):
    # Create directory if it doesn't exist
    if dictionary:
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        # Create full file path for results
        result_file_path = f'{folder_name}/{file_name}'

        # Write result to JSON file
        with open(result_file_path, 'w') as f:
            json.dump(dictionary, f)
    else:
        result_file_path = "no data for this file"

    return result_file_path


def read_stopwords(file_path):
    with open(file_path, 'r') as file:
        stopwords = {line.strip() for line in file if line.strip()}
    return stopwords
