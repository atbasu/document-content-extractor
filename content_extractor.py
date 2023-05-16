import json
import re

import openai


def get_prompt(text, config):
    prompt = 'The provided text is a closing confirmation of a loan generated for a property. From this piece of ' \
             'text, extract the values of the following fields: '
    for field, properties in config.items():
        prompt += f'{field}: {properties["description"]}\n'
    prompt += f"In the above list, the name of each field is succeeded by a description of the field " \
              f"after a ':'. It is not necessary that the piece of text " \
              f"contains all this information.  In this case leave the value of that field blank. If no fields are " \
              f"extracted return an empty json\nReturn it in a format that can be converted into a " \
              f"ptyhon dictionary using json.loads where the field name is the key and extracted value is the value " \
              f"\nText:\n{text}"
    return prompt


def extract_content(text, config, api_key, model, results_folder, file_name, run_id):
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
        prompt = get_prompt(text, config)
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
