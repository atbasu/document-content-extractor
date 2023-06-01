import csv
import time
import uuid
from datetime import datetime

from ascii_output_generator import generate_ascii_table_from_json
from content_extractor import extract_content_async
from utils import *


def upload_and_process_document(
        file_folder,
        results_folder,
        file_path,
        api_key,
        model,
        config,
        config_path,
        run_id
):
    file_path = f"{file_folder}/{input('Enter name of file : ').strip()}" if file_path is None else file_path
    api_key = input("Enter Open AI api key: ").strip() if (
            api_key is None or api_key == "YOUR_API_KEY_HERE") else api_key
    print(f"Processing {file_path} provided using {api_key} and parser configuration from {config_path}")

    text = read_document(file_path)
    result = extract_content_async(
        event=dict(
            text=text,
            config=config,
            api_key=api_key,
            model=model,
            results_folder=results_folder,
            file_name=file_path.split('/')[-1],
            run_id=run_id
        ),
        context=None
    )
    result.update(
        dict(
            file_path=file_path,
            api_key=api_key,
            config=config,
        )
    )
    return result


def write_metrics(run_id, run_time, file_path, api_key, success_rate, usage, model, folder_name, file_name='metrics'):
    # Create the 'run metrics' folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Get the current date and time
    now = datetime.now()

    # Create the CSV file name with the current date and time
    file_name = f'{folder_name}/{file_name}.csv'

    # Write data to CSV file
    is_file_exists = os.path.isfile(file_name)
    with open(file_name, 'a') as f:
        fieldnames = ['run_id', 'time', 'file_path', 'api_key', 'model', 'run_time', 'success_rate', 'total_tokens',
                      'prompt_tokens', 'completion_tokens']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # Write header row if file doesn't exist
        if not is_file_exists:
            writer.writeheader()

        # Write data row
        writer.writerow(
            dict(
                run_id=run_id,
                time=now,
                file_path=file_path,
                api_key=api_key,
                model=model,
                run_time=run_time,
                success_rate=success_rate,
                total_tokens=usage['total_tokens'],
                prompt_tokens=usage['prompt_tokens'],
                completion_tokens=usage['completion_tokens']
            )
        )

    return file_name


def check_for_errors(result):
    corrections = dict()
    # Ask the user if any values are incorrect
    user_input = input('Are any of the values incorrect? (y/n): ')
    while True:
        # Check if the user entered a valid input
        if user_input.lower() != 'y' and user_input.lower() != 'n':
            print('Invalid input. Please enter either y, n.')
            continue
        # If the user says values are incorrect
        elif user_input.lower() == 'y':
            # Ask the user for the field name that needs to be corrected
            field_names = input('Enter a coma separated list of fields that need to be corrected? ').split(',')
            # Check if the field name is valid
            for field_name in field_names:
                field_name = field_name.strip()
                if field_name not in result.keys():
                    print(f'{field_name} is an invalid field_name. Please enter a valid field name.')
                    continue
                # Ask the user for the correct value
                correct_value = input(f"What should the correct value be for {field_name}? ")
                # Add the correction to the corrections dictionary if the correct_vlaue doesn't match
                corrections[field_name] = correct_value if correct_value != result[field_name] else print(
                    'This value is the same as what was extracted, moving on to the next one.')
            # Ask the user if there are any other fields that need to be corrected
            user_input = input('Are there any other fields that need to be corrected? (y/n): ')
        # If the user says no values are incorrect, return 0
        else:
            return corrections


def run_app(file_path):
    run_id = uuid.uuid4().hex
    env_vars = read_env_vars()
    with open(env_vars['parser_config'], 'r') as f:
        config = json.load(f)

    start_time = time.monotonic()
    result = upload_and_process_document(
        file_folder=env_vars['file_folder'],
        results_folder=env_vars['results_folder'],
        file_path=file_path,
        api_key=env_vars['api_key'],
        model=env_vars['model'],
        config=config,
        config_path=env_vars['parser_config'],
        run_id=run_id
    )

    run_time = time.monotonic() - start_time
    result.update(
        dict(
            env=env_vars,
            run_id=run_id,
            run_time=run_time,
        )
    )
    return result


def main():
    # generate unique hex id for this run of the extractor
    run_id = uuid.uuid4().hex

    env_vars = read_env_vars()  # read all environment variables form config.ini
    args = read_args(env_vars['api_key'], env_vars['model'], env_vars['parser_config'], env_vars['splits'])
    model = args.model
    api_key = args.api_key
    file_path = args.file
    results_folder = env_vars['results_folder']
    with open(args.parser_config, 'r') as f:
        config = json.load(f)

    # start timer to calculate run time
    per_token_costs = {
        'text-davinci-003': 0.02 / 1000,
        'text-ada-001': 0.0004 / 1000,
        'text-babbage-001': 0.0005 / 1000,
        'text-curie-001': 0.002 / 1000
    }

    start_time = time.monotonic()
    result = upload_and_process_document(
        file_folder=env_vars['file_folder'],
        results_folder=results_folder,
        file_path=file_path,
        api_key=api_key,
        model=model,
        config=config,
        config_path=env_vars['parser_config'],
        run_id=run_id
    )
    file_path = result['file_path']
    # stop timer
    run_time = time.monotonic() - start_time
    if result['error'] is None:
        json_result = result['result']
        usage = result['usage_data']
        result_file = result['result_file']
        # print(json_result)
        # dump data into files and print result in ascii table
        ascii_table = generate_ascii_table_from_json(json_result, config)
        clear_screen()
        print(ascii_table)
        # check if there are any incorrect extractions
        corrections = check_for_errors(json_result)
        corrections_file = write_result_to_json(
            corrections,
            f"{file_path.split('/')[-1]}_corrections_{run_id}.json",
            results_folder
        )
        # calculate success rate as %age of fields that were extracted correctly
        success_rate = 100 - (len(corrections) / len(json_result) * 100)
        # store metrics in a csv file
        metrics_file = write_metrics(
            run_id,
            run_time,
            file_path,
            result['api_key'],
            success_rate,
            usage,
            model,
            env_vars['metrics_folder']
        )
        # store processing results in a json file
        # print run results
        clear_screen()
        print(
            f"File processing results:\n------------------------\n1. file : {file_path}\n2. metrics : {metrics_file}\n3. parsed results : {result_file}\n4. corrections : {corrections_file}\n5. cost : {usage['total_tokens'] * per_token_costs[args.model]}\n6. total run time : {run_time}")
    else:
        print(
            f"There was an error in processing this file:\n{result['error']['msg']}"
        )


if __name__ == '__main__':
    main()
