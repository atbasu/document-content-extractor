import csv
import uuid
from datetime import datetime

from ascii_output_generator import generate_ascii_table_from_json
from content_extractor import extract_content_async
from utils import *


def upload_and_process_document(
        file_folder,
        results_folder,
        doc_file_path,
        openai_api_key,
        openai_model,
        config,
        config_path,
        dce_run_id,
        dce_logger=None
):
    if dce_logger is not None:
        dce_logger.info("Starting document upload and processing")

    doc_file_path = f"{file_folder}/{input('Enter name of file : ').strip()}" if doc_file_path is None else doc_file_path
    openai_api_key = input("Enter Open AI api key: ").strip() if (
            openai_api_key is None or openai_api_key == "YOUR_API_KEY_HERE") else openai_api_key

    dce_logger.info(
        f"Processing {doc_file_path} provided using {openai_api_key} and parser configuration from {config_path}")

    text = read_document(doc_file_path)
    result = extract_content_async(
        event=dict(
            text=text,
            config=config,
            api_key=openai_api_key,
            model=openai_model,
            results_folder=results_folder,
            file_name=doc_file_path.split('/')[-1],
            run_id=dce_run_id
        ),
        logger=dce_logger
    )
    result.update(
        dict(
            file_path=doc_file_path,
            api_key=openai_api_key,
            config=config,
        )
    )

    if dce_logger is not None:
        dce_logger.info("Document upload and processing completed")
    return result


def write_metrics(
        dce_run_id,
        run_time,
        file_path,
        api_key,
        success_rate,
        usage,
        model,
        folder_name,
        file_name='metrics',
        logger=None
):
    if logger:
        logger.info("Writing metrics to CSV")

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
                run_id=dce_run_id,
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

    if logger:
        logger.info("Metrics written to CSV")
    return file_name


def check_for_errors(result, cleaned_text, config, env_vars, logger=None):
    if logger:
        logger.info("Validating output")

    corrections = dict()
    # Ask the user if any values are incorrect
    user_input = input('Are any of the values incorrect? (y/n): ')

    while True:
        # Check if the user entered a valid input
        if user_input.lower() != 'y' and user_input.lower() != 'n':
            print('Invalid input. Please enter either y, n.')
            user_input = input('Are there any other fields that need to be corrected? (y/n): ')
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
                correct_value = input(f"What should the correct value be for {field_name}?")
                if correct_value == result[field_name]:
                    print('This value is the same as what was extracted, moving on to the next one.')
                    continue
                # Ask the user for a justification
                justification = input(f"Why is this the correct value {field_name}?")
                # Add the correction to the corrections dictionary if the correct_vlaue doesn't match

                corrections[field_name] = dict(
                    correct_value=correct_value,
                    justification=justification
                )
            # Ask the user if there are any other fields that need to be corrected
            user_input = input('Are there any other fields that need to be corrected? (y/n): ')
        # If the user says no values are incorrect, return 0
        else:
            correction_prompt = ''
            if corrections:
                def filter_corrections(field, properties):
                    return field in corrections.keys()

                fields = get_formatted_prompt_fields(config, filter_func=filter_corrections)
                prompt = format_prompt(env_vars["prefix"], fields, env_vars["midfix"], cleaned_text, env_vars["suffix"])
                returned_values = ''
                correct_values = ''
                for key, value in corrections.items():
                    returned_values += f"{key} : {result[key]}\n"
                    correct_values += f"{key} : {value['correct_value']}\n{value['justification']}\n"
                correction_prompt = f"I am using the open AI completion api to to process the following prompt:\n" \
                                    f"----------------------\n{prompt}\n----------------------\nHowever, the value" \
                                    f" of the following fields were extracted incorrectly:\n{returned_values}\nit" \
                                    f" should be returning:\n{correct_values}\nHow can the definition of the wrongly" \
                                    " extracted fields be corrected in the prompt to extract the right values?"

            return corrections, correction_prompt


def run_app(file_path, console_log_level, app_logger=None):
    if app_logger:
        app_logger.info("Running the application")
    dce_run_id = uuid.uuid4().hex
    # Set up logging
    dce_logger = setup_logging(dce_run_id, console_log_level)

    env_vars = read_env_vars()
    with open(env_vars['parser_config'], 'r') as f:
        config = json.load(f)

    start_time = time.monotonic()
    result = upload_and_process_document(
        file_folder=env_vars['file_folder'],
        results_folder=env_vars['results_folder'],
        doc_file_path=file_path,
        openai_api_key=env_vars['api_key'],
        openai_model=env_vars['model'],
        config=config,
        config_path=env_vars['parser_config'],
        dce_run_id=dce_run_id,
        dce_logger=dce_logger
    )

    run_time = time.monotonic() - start_time
    result.update(
        dict(
            env=env_vars,
            run_id=dce_run_id,
            run_time=run_time
        )
    )
    if app_logger:
        app_logger.info(f"Exiting application after running for {run_time}s with result : {result}")
    return result


def main():
    # generate unique hex id for this run of the extractor
    run_id = uuid.uuid4().hex

    # read all environment variables form config.ini
    env_vars = read_env_vars()
    args = read_args(env_vars['api_key'], env_vars['model'], env_vars['parser_config'], env_vars['splits'])
    model = args.model
    api_key = args.api_key
    file_path = args.file
    results_folder = env_vars['results_folder']
    with open(args.parser_config, 'r') as f:
        config = json.load(f)

    # Set up logging
    dce_logger = setup_logging(run_id, args.log_level)

    per_token_costs = {
        'text-davinci-003': 0.02 / 1000,
        'text-ada-001': 0.0004 / 1000,
        'text-babbage-001': 0.0005 / 1000,
        'text-curie-001': 0.002 / 1000
    }

    # start timer to calculate run time
    start_time = time.monotonic()
    result = upload_and_process_document(
        file_folder=env_vars['file_folder'],
        results_folder=results_folder,
        doc_file_path=file_path,
        openai_api_key=api_key,
        openai_model=model,
        config=config,
        config_path=env_vars['parser_config'],
        dce_run_id=run_id,
        dce_logger=dce_logger
    )
    file_path = result['file_path']
    # stop timer
    run_time = time.monotonic() - start_time
    # print(result)
    result['result_file'] = write_result_to_json(result, result['result_file'], results_folder)

    if result['error'] is None:
        json_result = result['result']
        usage = result['usage_data']
        result_file = result['result_file']
        # print(json_result)
        # dump data into files and print result in ascii table
        ascii_table = generate_ascii_table_from_json(json_result, config, dce_logger)
        clear_screen()
        print(ascii_table)
        # check if there are any incorrect extractions
        corrections, correction_prompt = check_for_errors(
            result=json_result,
            cleaned_text=result['cleaned_text'],
            config=config,
            env_vars=env_vars,
            logger=dce_logger
        )
        corrections_file = ''
        correction_prompt_file_name = ''
        if corrections:
            corrections_file = write_result_to_json(
                corrections,
                f"{file_path.split('/')[-1]}_corrections_{run_id}.json",
                results_folder
            )
            correction_prompt_file_name = f"{results_folder}/{file_path.split('/')[-1]}_corrections_prompt_{run_id}.txt"
            with open(correction_prompt_file_name, 'w') as outfile:
                outfile.write(correction_prompt)

        # calculate success rate as %age of fields that were extracted correctly
        success_rate = 100 - (len(corrections) / len(json_result) * 100)
        # store metrics in a csv file
        metrics_file = write_metrics(
            dce_run_id=run_id,
            run_time=run_time,
            file_path=file_path,
            api_key=result['api_key'],
            success_rate=success_rate,
            usage=usage,
            model=model,
            folder_name=env_vars['metrics_folder'],
            file_name='metrics',
            logger=dce_logger
        )
        # store processing results in a json file
        # print run results
        clear_screen()
        print(
            f"File processing results:\n------------------------\n1. file : {file_path}\n2. metrics : {metrics_file}\n3. parsed results : {result_file}\n4. corrections : {corrections_file}\n\t- You can enter the prompt in {correction_prompt_file_name} in Chat GPT(https://chat.openai.com/) to identify fixes for the errors\n5. cost : {usage['total_tokens'] * per_token_costs[args.model]}\n6. total run time : {run_time}")
    else:
        print(
            f"There was an error in processing this file:\n{result['error']['msg']}"
        )


if __name__ == '__main__':
    main()
