import asyncio
import json
import re
from collections import defaultdict

import aiohttp
import openai


def get_prompt_old(text, config):
    prompt = f"Extract the values of the following fields from the closing confirmation text:\n"
    prompt += '\n'.join(
        [f'|{field}|: |{properties["description"]}|' for field, properties in config.items() if properties["required"]])
    prompt += f"\nEnclose both the field name and the value in |.\nText:\n{text}"
    return prompt


def get_prompts(text, config, splits=1):
    # only get those fields where required is set to true
    fields = [f'[{field}]: [{properties["description"]}]' for field, properties in config.items() if
              properties["required"]]

    # split the fields into chunks where number of chunks = splits
    num_fields = len(fields)
    splits = min(splits, num_fields)
    chunk_size = num_fields // splits

    # generate prompts using each chunk so that number of prompts  = splits
    prompts = [
        f"Extract the values of the following fields from the closing confirmation text:\n" + '\n'.join(
            fields[i * chunk_size:(i + 1) * chunk_size]) +
        f"\nEnclose both the field name and the value in square brackets.\nText:\n{text}"
        for i in range(splits)
    ]

    return prompts


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


async def process_chunk(prompt, model, api_key):
    async with aiohttp.ClientSession() as session:
        openai.api_key = api_key

        response = await session.post(
            f'https://api.openai.com/v1/engines/{model}/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            json={
                'prompt': prompt,
                'max_tokens': 2000,
                'temperature': 0.7,
                'top_p': 1,
                'frequency_penalty': 0,
                'presence_penalty': 0,
                'echo': False
            }
        )

        result = await response.json()
        return result


async def process_text(text, config, chunk_size, model, api_key):
    # chunks = create_word_chunks(text, max_words)
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    tasks = []
    async with aiohttp.ClientSession() as session:
        for chunk in chunks:
            prompt = get_prompts(chunk, config)
            task = asyncio.ensure_future(process_chunk(prompt, model, api_key))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return responses


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


async def process_prompts(text, config, splits, model, api_key):
    # get all the prompts that need to be queried
    prompts = get_prompts(text, config, splits)

    tasks = []
    # query prompts asynchronously
    async with aiohttp.ClientSession() as session:
        for prompt in prompts:
            task = asyncio.ensure_future(process_chunk(prompt, model, api_key))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        return prompts, responses


def process_results(prompts, results):
    # process response by:
    # 1. creating an output text file containing all prompts and entire response
    # 2. extracting all key value pairs in the format [..]: [...]
    # 3. generating usage statistics
    # return all three
    output_file = ''
    output_dict = dict()
    usage_dict = defaultdict(int)
    pattern = r'\[(.*?)\]:\s*\[(.*?)\]'

    for i, (prompt, response) in enumerate(zip(prompts, results)):
        output_file += f'----------------[prompt {i + 1}]------------------\n{prompt}\n[response {i + 1}]\n{response}\n----------------------------------\n'
        matches = re.findall(pattern, response["choices"][0]["text"])
        output_dict.update({key.strip(): value.strip() for key, value in matches})
        for key, value in response["usage"].items():
            usage_dict[key] += value

    usage_dict = dict(usage_dict)

    return output_file, output_dict, usage_dict


def extract_content_async(text, config, api_key, model, results_folder, file_name, run_id, splits=1):
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
