import asyncio
import traceback
from collections import defaultdict

import aiohttp
import openai
from transformers import GPT2Tokenizer

from utils import read_env_vars, read_stopwords, format_prompt, get_formatted_prompt_fields

# unused code in the section below, but kept for future testing
'''
def get_prompt_old(text, config):
    prompt = f"Extract the values of the following fields from the closing confirmation text:\n"
    prompt += '\n'.join(
        [f'|{field}|: |{properties["description"]}|' for field, properties in config.items() if properties["required"]])
    prompt += f"\nEnclose both the field name and the value in |.\nText:\n{text}"
    return prompt


def get_prompt_new(text, config):
    prompt = 'Extract the values of the following fields from the closing confirmation text:'
    for field, properties in config.items():
        prompt += f'"{field}": {properties["description"]}\n'
    prompt += f"\nEnclose both the field name and the value in double quotes and return the entire output within " \
              f"curly braces.\nText:\n{text}"
    return prompt
    
    
def create_word_chunks(text, max_words):
    words = re.findall(r'\S+\s*', text)

    chunked_text = []
    current_chunk = ""
    current_word_count = 0

    for word in words:
        if current_word_count + 1 <= max_words:
            current_chunk += word
            current_word_count += 1
        else:
            chunked_text.append(current_chunk)
            current_chunk = word
            current_word_count = 1

    if current_chunk:
        chunked_text.append(current_chunk)

    return chunked_text
    


async def process_text(text, config, chunk_size, model, api_key, retry_delay=1, max_retries=3):
    # chunks = create_word_chunks(text, max_words)
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    tasks = []
    prompts = []
    async with aiohttp.ClientSession() as session:
        for chunk in chunks:
            prompt = get_prompts(chunk, config)
            prompts.append(prompt)
            task = asyncio.ensure_future(process_chunk(prompt, model, api_key, retry_delay, max_retries))
            tasks.append(task)

        try:
            responses = await asyncio.gather(*tasks)
            return prompts, responses
        except (OpenAIException, Exception) as e:
            # Return the exception object
            return prompts, e


def extract_content_with_chunking(text, config, api_key, model, results_folder, file_name, run_id):
    prompt = ""

    response = dict()
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(process_text(text, config, 1000, model, api_key))
    agg_result = {
        "result": {},
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0
    }
    temp_dicts = []
    for result in results:
        temp_dicts.append(json.loads(re.sub(r'[^\x00-\x7f]', r'', result["choices"][0]["text"].strip())))
        agg_result["prompt_tokens"] += result['usage']['total_tokens']

    # TODO : function doesn't work below this point, needs to be fixed to handle results instead of response
    file_name = f'{results_folder}/{file_name}_run_results_{run_id}.json'

    response_dict = response.to_dict()
    response_dict["prompt"] = prompt

    with open(file_name, 'w') as outfile:
        json.dump(response_dict, outfile)

    # return response
    result = json.loads(response["choices"][0]["text"].replace("\\", "").strip()) if api_key == "test" else \
        json.loads(re.sub(r'[^\x00-\x7f]', r'', response.choices[0].text.strip()))

    return result, response["usage"], file_name


def extract_content_test(text, config, api_key, model, results_folder, file_name, run_id):
    prompt = ""
    if api_key == "test":
        response = json.loads("""
            {
                "choices": [
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "logprobs": null,
                        "text": "{\\"Signer name\\": \\"CARTER\\\\THOMAS J.\\", \\"email\\": null, \\"phone number\\": \\"(803)316-7103\\", \\"Is the signer a foreign national?\\": null, \\"Language\\": null, \\"Timezone\\": \\"EST\\", \\"Property address\\": \\"1006 FURMAN DRIVE, SUMTER, SC - 29154\\", \\"Appointment address\\": \\"1006 FURMAN DRIVE, SUMTER, SC - 29154\\", \\"Appointment Date and Time\\": null, \\"File Number\\": \\"01-01711646\\", \\"Order on behalf of\\": null, \\"Signing type\\": null, \\"Product type\\": null, \\"Company Fee\\": \\"$300.00\\", \\"Client\\": null, \\"Agent\\": \\"CAROLINA ATTORNEY NETWORK, LLC\\", \\"Agent Fee\\": null, \\"Witness Number\\": null, \\"Upload Files\\": null, \\"Internal Notes\\": null, \\"External notes\\": \\"Please read and comply with our specific instructions which will be sent with the closing\\\\npackage. Do not give any opinion regarding fees being too high or too low. PLEASE\\\\nCONFIRM APPOINTMENT WITH BORROWER upon receipt of this confirmation. If all parties are\\\\nnot present or any other issues exist that require clarification, please contact us at the\\\\ntelephone numbers sent with the specific instructions in the closing package. If you have\\\\nquestions regarding this assignment, please contact our Scheduling Department at\\\\n631-715-3492.\\\\n\\\\nDO NOT CHANGE THE CLOSING TIME WITH THE BORROWER.\\\\nYOU MUST CONTACT OUR OFFICE IF YOU HAVE ANY ISSUES WITH THE SCHEDULED CLOSING TIME AT\\\\n(631)715-3492.\\", \\"Instruction type\\": null, \\"Instructions\\": null, \\"Scan Backs Needed\\": null}"
                    }
                ],
                "created": 1683287044,
                "id": "cmpl-7Co8yh90yc1N5Xdkk7XSY9YGtYjyI",
                "model": "text-davinci-003",
                "object": "text_completion",
                "usage": {
                    "completion_tokens": 45,
                    "prompt_tokens": 1286,
                    "total_tokens": 1331
                }
            }
        """)
    else:
        prompt = get_prompts(text, config)
        # return prompt

        openai.api_key = api_key

        # Process text using OpenAI API
        response = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            echo=False
        )

    file_name = f'{results_folder}/{file_name}_run_results_{run_id}.json'

    response_dict = response.to_dict()
    response_dict["prompt"] = prompt

    with open(file_name, 'w') as outfile:
        json.dump(response_dict, outfile)

    # return response
    result = json.loads(response["choices"][0]["text"].replace("\\", "").strip()) if api_key == "test" else json.loads(
        re.sub(r'[^\x00-\x7f]', r'', response.choices[0].text.strip()))

    return result, response["usage"], file_name
    

def extract_kv(match):
    key = ''
    value = ''
    for item in match:
        if key == '' and item != '':
            key = item.strip().strip('[]')
        elif key != '' and value == '' and item != '':
            value = item.strip().strip('[]')
    return {key: value}
    
    
def extract_content_async_old(text, config, api_key, model, results_folder, file_name, run_id, splits=1):
    loop = asyncio.get_event_loop()
    prompts, results = loop.run_until_complete(process_prompts(text, config, splits, model, api_key))

    output_file, result, usage_data = process_results(prompts, results)

    # write results to file
    file_name = f'{results_folder}/{file_name}_run_results_{run_id}.txt'
    with open(file_name, 'w') as outfile:
        outfile.write(output_file)

    return result, usage_data, file_name


def extract_content(text, config, api_key, model, results_folder, file_name, run_id):
    prompt = get_prompts(text, config)[0]
    # return prompt

    openai.api_key = api_key

    # Process text using OpenAI API
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=1000,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        echo=False
    )

    file_name = f'{results_folder}/{file_name}_run_results_{run_id}.json'

    response_dict = response.to_dict()
    response_dict["prompt"] = prompt

    with open(file_name, 'w') as outfile:
        json.dump(response_dict, outfile)

    # process response
    # sometimes the response will return with some leading and trailing characters that are not relevant to the output
    # Extract the portion between '{' and '}'

    start_index = text.find('{')
    end_index = text.rfind('}')
    trimmed_text = response.choices[0].text.strip()[start_index:end_index + 1]

    # sometimes the text will contain characters that cannot be parsed by json.loads
    cleaned_text = re.sub(r'[^\x00-\x7f]', r'', trimmed_text)

    # convert the text into a dictionary to return
    result = json.loads(cleaned_text)

    return result, response["usage"], file_name


text_blob_new = '\nhappy go lucky Appointment Date and Time : 10/12/2022 10:00 AM\nFile Number: ORG-369006\nOrder on behalf of : DEANNA GOOD, Product type : Home Equity Loan\n'

def extract_values_old(text, keys):
    result = {}
    keys = list(keys)
    for i, key in enumerate(keys):
        start_index = text.find(key)
        if start_index != -1:
            start_index += len(key) + 2  # Skip the key and the colon, accounting for the space after colon
            if i < len(keys) - 1:
                end_index = text.find(keys[i + 1], start_index)
            else:
                end_index = len(text)
            value = text[start_index:end_index].strip().split(',')[0]
            result[key] = value
    return result

'''


def clean_prompt(prompt_text, prompt_padding, max_tokens=2048, prompt_threshold=150, stop_words=None, logger=None):
    # Initialize the tokenizer
    if stop_words is None:
        stop_words = set()
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    # Tokenize the text
    prompt_tokens = tokenizer.tokenize(prompt_text)
    # print(stop_words)
    padding_tokens = tokenizer.tokenize(prompt_padding)
    # Remove stop words
    max_tokens = max(max_tokens - len(padding_tokens), 0)
    # clean the prompt if it exceeds the max_tokens limit
    if len(prompt_tokens) >= max_tokens:
        prompt_tokens = [token for token in prompt_tokens if token.lower() not in stop_words]
    # Truncate the prompt if it still exceeds the max_tokens limit
    if len(prompt_tokens) - max_tokens < prompt_threshold:
        prompt_tokens = prompt_tokens[:max_tokens]

    # Join the tokens back into a text string
    cleaned_text = tokenizer.convert_tokens_to_string(prompt_tokens)

    if logger:
        logger.debug("Cleaned prompt: %s", cleaned_text)

    return cleaned_text


def get_prompts(event, env_vars, logger=None):
    text = event['text']
    config = event['config']

    splits = env_vars['splits']
    prefix = env_vars['prefix']
    midfix = env_vars['midfix']
    suffix = env_vars['suffix']
    max_tokens = env_vars['max_tokens']
    prompt_threshold = env_vars['prompt_threshold']
    stopwords_file = env_vars['stopwords']

    # only get those fields where required is set to true
    def is_required(field, properties):
        return properties["required"]

    fields = get_formatted_prompt_fields(config, is_required)

    # split the fields into chunks where number of chunks = splits
    num_fields = len(fields)
    splits = min(splits, num_fields)
    chunk_size = num_fields // splits
    default_stopwords = read_stopwords(stopwords_file)

    cleaned_text = clean_prompt(text, prefix + suffix + midfix, max_tokens, prompt_threshold, default_stopwords, logger)

    # generate prompts using each chunk so that number of prompts  = splits
    prompts = [
        format_prompt(prefix, fields[i * chunk_size:(i + 1) * chunk_size], midfix, cleaned_text, suffix)
        for i in range(splits)
    ]

    return prompts, cleaned_text


class OpenAIException(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{status_code} - {message}")


async def process_chunk(prompt, model, api_key, retry_delay=1, max_retries=3, response_tokens=500, logger=None):
    async with aiohttp.ClientSession() as session:
        openai.api_key = api_key
        retries = 0

        while retries <= max_retries:
            response = await session.post(
                f'https://api.openai.com/v1/engines/{model}/completions',
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                },
                json={
                    'prompt': prompt,
                    'max_tokens': response_tokens,
                    'temperature': 0.7,
                    'top_p': 1,
                    'frequency_penalty': 0,
                    'presence_penalty': 0,
                    'echo': False
                }
            )

            if response.status == 200:
                result = await response.json()
                return result
            elif response.status == 500:
                retries += 1
                if retries <= max_retries:
                    await asyncio.sleep(retry_delay)  # Delay before retrying
                else:
                    error_message = await response.text()
                    raise OpenAIException(
                        500,
                        f"The server had an error while processing your request. We retried your request after a {retry_delay}s  delay {max_retries} times but the error persisted. Contact OpenAI for this issue. Error: {error_message}"
                    )
            else:
                error_message = await response.text()
                if response.status == 401:
                    if "Invalid Authentication" in error_message:
                        raise OpenAIException(
                            401,
                            "Invalid Authentication: Ensure the correct API key and requesting organization are being "
                            "used."
                        )
                    elif "Incorrect API key provided" in error_message:
                        raise OpenAIException(
                            401,
                            "Incorrect API key provided: Ensure the API key used is correct, clear your browser "
                            "cache, or generate a new one."
                        )
                    elif "You must be a member of an organization to use the API" in error_message:
                        raise OpenAIException(
                            401,
                            "You must be a member of an organization to use the API: Contact us to get added to a new "
                            "organization or ask your organization manager to invite you."
                        )
                elif response.status == 429:
                    if "Rate limit reached for requests" in error_message:
                        raise OpenAIException(
                            429,
                            "Rate limit reached for requests: Pace your requests. Read the Rate limit guide."
                        )
                    elif "You exceeded your current quota, please check your plan and billing details" in error_message:
                        raise OpenAIException(
                            429,
                            "You exceeded your current quota, please check your plan and billing details: Apply for a "
                            "quota increase."
                        )
                    elif "The engine is currently overloaded, please try again later" in error_message:
                        raise OpenAIException(
                            429,
                            "The engine is currently overloaded, please try again later: Please retry your requests "
                            "after a brief wait."
                        )
                else:
                    raise OpenAIException(response.status, error_message)


async def process_prompts(event, env_vars, logger=None):
    # get all the prompts that need to be queried
    prompts, cleaned_text = get_prompts(event=event, env_vars=env_vars, logger=logger)

    tasks = []
    # query prompts asynchronously
    async with aiohttp.ClientSession() as session:
        for prompt in prompts:
            task = asyncio.ensure_future(
                process_chunk(
                    prompt=prompt,
                    model=event['model'],
                    api_key=event['api_key'],
                    retry_delay=env_vars['retry_delay'],
                    max_retries=env_vars['max_retries'],
                    response_tokens=env_vars['response_tokens'],
                    logger=logger
                )
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return prompts, responses, cleaned_text


def extract_values(text):
    # Split the text into lines
    lines = text.split('\n')
    # Create an empty dictionary to store the key-value pairs
    data_dict = {}
    # Process each line
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            # Strip any leading/trailing whitespace from the key and value
            key = key.strip()
            value = value.strip()
            data_dict[key] = value
    return data_dict


def process_results(prompts, results, logger=None):
    # process response by:
    # 1. log all prompts and entire response
    # 2. extracting all key value pairs in the format [..]: [...]
    # 3. generating usage statistics
    # return last two
    output_dict = dict()
    usage_dict = defaultdict(int)
    # pattern = r'\[(.*?)\]:\s*\[(.*?)\]'
    # pattern = r'\[\s*(.*?)\s*\]:\s*(?:\[(.*?)\]|([^\[\]\n]*))|(?:\s*(.*?)\s*:\s*\[(.*?)\])'

    for i, (prompt, response) in enumerate(zip(prompts, results)):
        if logger:
            logger.info(f"[prompt {i + 1}]: {prompt}")
            logger.info(f"[response {i + 1}]: {response}")

        output_dict.update(extract_values(response["choices"][0]["text"]))

        for key, value in response["usage"].items():
            usage_dict[key] += value

    usage_dict = dict(usage_dict)

    return output_dict, usage_dict


def extract_content_async(event, logger=None):
    env_vars = read_env_vars(
        ["splits", "retry_delay", "max_retries", "prefix", "midfix", "suffix", "max_tokens", "prompt_threshold",
         "stopwords", "response_tokens"]
    )
    config = event['config']
    try:
        loop = asyncio.get_event_loop()
        prompts, results, cleaned_text = loop.run_until_complete(
            process_prompts(
                event=event,
                env_vars=env_vars,
                logger=logger
            )
        )

        result, usage_data = process_results(prompts, results, logger)

        return {
            'result': result,
            'cleaned_text': cleaned_text,
            'usage_data': usage_data,
            'result_file': f"{event['file_name']}_run_results_{event['run_id']}.json",
            'error': None
        }
    except OpenAIException as e:
        error_message = f"OpenAI API Exception: {traceback.format_exc()}"
        if logger is not None:
            logger.error(error_message)
        # Return the error message and exception object
        return {
            'result': None,
            'cleaned_text': None,
            'usage_data': None,
            'result_file': None,
            'error': dict(
                exception=e,
                msg=error_message
            )
        }
    except Exception as e:
        error_message = f"Unexpected Exception: {traceback.format_exc()}"
        if logger is not None:
            logger.error(error_message)
        # Return the error message and exception object
        return {
            'result': None,
            'cleaned_text': None,
            'usage_data': None,
            'result_file': None,
            'error': dict(
                exception=e,
                msg=error_message
            )
        }
