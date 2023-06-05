# Document Content Extractor
_descroption of the tool coming soon_

## Getting Started with the CLI

Step 1. download the project code
Step 2. install the latest version of python
Step 3. Install necessary requirements:
```
pip3 install -r requirements.txt
```
Step 4. in the project directory create three folders as defined in the config.ini file
Step 5. update the key and other settings in the config.ini file
Step 6.1.  move a pdf file that you want to parse into the `sample forms` folder
Step 7.1. run the program:
```
python document-content-extractor.py
```

### Potential Issues:

### ClientConnectorCertificateError

After running the app, you may run into the following error:
```
Processing sample forms/01-01711646.pdf provided using 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 and parser configuration from closewise_parser_configurator.json
Traceback (most recent call last):
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/aiohttp/connector.py", line 980, in _wrap_create_connection
    return await self._loop.create_connection(*args, **kwargs)  # type: ignore[return-value]  # noqa
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/base_events.py", line 1112, in create_connection
    transport, protocol = await self._create_connection_transport(
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/base_events.py", line 1145, in _create_connection_transport
    await waiter
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/sslproto.py", line 574, in _on_handshake_complete
    raise handshake_exc
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/sslproto.py", line 556, in _do_handshake
    self._sslobj.do_handshake()
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/ssl.py", line 979, in do_handshake
    self._sslobj.do_handshake()
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1002)

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/akhileshthapliyal/document-content-extractor/document-content-extractor.py", line 244, in <module>
    main()
  File "/Users/akhileshthapliyal/document-content-extractor/document-content-extractor.py", line 207, in main
    file_path, api_key, json_result, config, usage, result_file = upload_and_process_document(
                                                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/akhileshthapliyal/document-content-extractor/document-content-extractor.py", line 60, in upload_and_process_document
    result = extract_content_async(
             ^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/akhileshthapliyal/document-content-extractor/content_extractor.py", line 294, in extract_content_async
    prompts, results = loop.run_until_complete(
                       ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/asyncio/base_events.py", line 653, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/Users/akhileshthapliyal/document-content-extractor/content_extractor.py", line 211, in process_prompts
    responses = await asyncio.gather(*tasks)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/akhileshthapliyal/document-content-extractor/content_extractor.py", line 74, in process_chunk
    response = await session.post(
               ^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/aiohttp/client.py", line 536, in _request
    conn = await self._connector.connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/aiohttp/connector.py", line 540, in connect
    proto = await self._create_connection(req, traces, timeout)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/aiohttp/connector.py", line 901, in _create_connection
    _, proto = await self._create_direct_connection(req, traces, timeout)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/aiohttp/connector.py", line 1206, in _create_direct_connection
    raise last_exc
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/aiohttp/connector.py", line 1175, in _create_direct_connection
    transp, proto = await self._wrap_create_connection(
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/aiohttp/connector.py", line 982, in _wrap_create_connection
    raise ClientConnectorCertificateError(req.connection_key, exc) from exc
aiohttp.client_exceptions.ClientConnectorCertificateError: Cannot connect to host api.openai.com:443 ssl:True
```
The error message you're encountering indicates an SSL certificate verification failure. This issue usually occurs when the SSL certificate of the server you're trying to connect to cannot be verified or trusted by the Python installation on your computer.

Here are a few steps you can try to resolve the issue:

1. Update Python: Ensure that your Python installation is up to date. You can do this by running the following command in the terminal:
   ```
   python3 -m pip install --upgrade pip
   ```

2. Install Certificates: Try installing or updating the certificates on your computer. You can do this by running the following command in the terminal on a mac:
   ```
   /Applications/Python\ {version}/Install\ Certificates.command
   ```
   Replace `{version}` with the specific Python version you are using, such as `3.11` in your case.

3. Check the SSL Configuration: Verify that the SSL configuration on your computer is correct. Ensure that the CA (Certificate Authority) certificates are installed and up to date. You can typically find these certificates in the `/usr/local/etc/openssl/cert.pem` file on a mac.

-----

## Using the API

Step 6.2. Once you've completed step 5 in Getting started with the CLI, then start the app with the command:
```
(venv) (base) atbasu@x86_64-apple-darwin13 document-content-extractor % python3.11 app.py
```
if all goes well, this should kickstart the api on `http://127.0.0.1:5000` and you should see the following on your terminal:
```
 * Serving Flask app 'app'
 * Debug mode: on
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
INFO:werkzeug:Press CTRL+C to quit
INFO:werkzeug: * Restarting with stat
WARNING:werkzeug: * Debugger is active!
INFO:werkzeug: * Debugger PIN: 540-404-850
```
Step 7.2 Now you can use your favoriate api invocation method. To test we recommend trying it with postman.
_screenshots coming soon_

### API input
_coming soon_

### API output

The api will always return a dictionary with the following keys:
```
{
  'result' : None if there was an error processing the request otherwise it is a dictinoary whose keys are each of the fields to be extracted, and the value is the extracted content from the file
  'usage_data': None if there was an error processing the request otherwise it is a dictinoary whose keys are:
total_tokens, prompt_tokens, response_tokens
  'result_file': None if there is an error otherwise it's location where the results of each prompt is stored for analysis
  'error': None if there a valid resonse otherewise it's another dictionary with the keys exception which contains the exceoption object, and msg whch contains the processed traceback message.
  'file_path': path of the file that was read,
  'api_key': Open AI api key used to run the query,
  'config': the parser configuration used to generate the query prompts,
  'emv' : a dictinoary containig all the environment variables used in processing the query,
  'run_id': unique hexadecial identifier generated when each query is processed,
  'run_time': time taken in second for open ai apis to process the queryies and return a result
}
```
----

## Fine tuning the adapter

There are three ways to fine tune the adapter:
1. Updating the config.ini file with the appropriate parameters required for your extractor
2. Modifying the parser config file to define what you want extracted
3. Editing the stopwords list

### 1. config.ini

The `config.ini` file allows you to fine-tune the parameters of the exteactor, such as API key, model selection, folder paths, and various settings related to prompt generation and extraction. Make sure to update the necessary values and paths based on your specific extractor requirements.

Here's a breakdown of the parameters defined in the file:

**[openai] section:**
- `api_key`: Specifies the API key to be used for OpenAI services. Replace "YOUR_API_KEY_HERE" with the actual API key. To generate an api key follow the instructions [here](https://www.howtogeek.com/885918/how-to-get-an-openai-api-key/).
- `model`: Sets the model to be used by OpenAI. By default the "text-davinci-003" is selected. For more information on what models are avaialable and the cost of using each model head over to the OpenAI API reference documentation [here](https://platform.openai.com/docs/models/gpt-3).
- `retry_delay`: Defines the delay (in seconds) between retry attempts after a server error when the OpenAI apis is called. It is set to 1 second by default. 
- `max_retries`: Indicates the maximum number of times the extractor will retry the OpenAI Api in case of server error before giving up. By default it is set to 3.

**[extractor] section:**
- `file_folder`: Specifies the folder where the documents to be parsed are located.
- `results_folder`: Sets the folder where the results of the extraction process will be stored.
- `metrics_folder`: Defines the folder where the metrics related to the extraction process will be stored.
- `parser_config`: Specifies the JSON file that contains the configuration for the parser. Modifying this parser will change what information the extractor looks for in the file being parsed. See the next section for a more detailed overview of this fiel.

**[prompt_eng] section:**
- `prefix`: Defines the prefix text to be used when generating prompts for extracting field values from parsed file.
- `midfix`: Specifies the midfix text to be used when generating prompts for extraction.
- `suffix`: Specifies the suffix text to be used when generating prompts for extraction.
- `max_chunk`: Sets the maximum chunk size (in characters) for each prompt generated.
- `splits`: Indicates the number of splits to divide the prompt into when generating from the parser_config file. E.g. if there are 15 fields defined in the parser_config that need to be extracted by the extractor, and the number of splits is set to 3, then when generating the prompts, the fields will be split into 3 groups and each group will be used to e generate a separate prompt that will be queried asynchronously. Increasing number of splits can improve response time from the api by leveraging parallel processing, but it will also increase the cost of processsing the document as the text of the file to be parsed will be repeated in each prompt.
- `max_tokens`: Defines the maximum number of tokens allowed for a single prompt. By default this is set to the maximum possible tokens that the OpenAI apis will process.
- `response_tokens`: Sets the number of tokens reserved for the response generated by the model. Depending on how many fields are extracted in each prompt(determined by the number of `splits`), this size will vary. If there are more fields extracted in each prompt, the response_tokens will have to increase to ensure the response contains all the values for each field. However, increasing this number will reduce the number of tokens for the prompt itself, as the `max_tokens` must be a sum of the `response_tokens` and the tokens in the prompt.
- `prompt_threshold`: Specifies the threshold (in tokens) for the total number of tokens to exceed max_tokens and still be processed. if the prompt and the response exceeds max_tokens by this threshold then the extractor will fail and report an error to the user. However, if it is less than the threshold then the extractor will truncate the prompt by chopping off the excess tokens from the end of the file to be parsed and then processing the text. This threshold should be set to greater than 0 if you're sure that the last few characters of text from the file to be parsed are not useful.
- `stopwords`: Specifies the file containing stopwords, which are words to be excluded from the prompt generation process. For more information on this file refer to the section below.

## 2. parser_config

The `parser_config` file is used in conjunction with the provided code to generate prompts for querying the OpenAI API. By understanding the structure of the `parser_config` file and how it is used in conjunction with the provided code, you can customize the fields to extract and generate prompts accordingly. Remember to update the `parser_config` file and adjust the code as needed to suit your specific use case.

Here's a summary of how the `parser_config` file is used and how it can be modified:

1. **Usage**: The `parser_config` file is a JSON file that defines the fields to extract from the closing confirmation text. Each field has the following properties:
   - `type`: Specifies the data type of the field.
   - `required`: Indicates whether the field is required for extraction. If the value is set to false, then this field will be ignored during prompt generation.
   - `description`: Provides a description of the field. The more articulate this description, the more likely OpenAI will be able to extract the correct values. However, the more verbose this description, the longer the prompt becomes resulting in increased cose.

2. **Modifying the `parser_config`**: To modify the `parser_config` file, you can follow these steps:
   - Add or remove fields: You can add or remove fields by adding or deleting key-value pairs in the JSON file. Each field should have a unique name. In case you think a field might be useful in the future, but you don't need it right now, instead of deleting it, you can simply set the `required` value to false.
   - Modify field properties: You can update the `type`, `required`, or `description` properties for each field to match your specific requirements.

3. **Generating Prompts**: The provided code utilizes the `parser_config` file to generate prompts for extracting field values. The code reads the `parser_config` and selects fields where `required` is set to `true`. It then splits the selected fields into chunks based on the `splits` value specified in the `config.ini` file.

4. **Prompt Generation**: The [prompts are generated](https://github.com/atbasu/document-content-extractor/blob/3780420e1f71ff93059c3c635951d41eaa17f3c9/content_extractor.py#L261) by concatenating the selected fields for each chunk. The resulting prompts follow a specific format:
   - Prefix: The value is set in the `config.ini` file and forms the first part of the prompt.
   - Field list: After the prefix, each field is listed along with its description.
   - Midfix: The midfix text specified in the `config.ini` file is then added to the prompt
   - Text: The text of the file to be parsed is then added to the prompt.
   - Suffix: Finally the suffix text specified in the `config.ini` file is added to the prompt.

5. **Prompt Customization**: If you want to modify the prompt generation process, you can update the values in the `config.ini` file. The parameters that control prompt generation include `prefix`, `midfix`, `suffix`, `max_tokens`, `prompt_threshold`, and `stopwords_file`. Adjusting these parameters allows you to fine-tune the prompts based on your project requirements.


## 2. stopwords

The stopwords file is a text file used in the prompt clean up process. If a prompt is too long, the OpenAI api will refuse to process the prompt. So to workaround that, one of the steps is to eliminate unnecessary words in the prompt. The stopwords file specified in `config.ini` contains a list of words or phrases in each new line of the file, which will be eliminated from the prompt if found. e.g. if the file looks like this:
```
from
you
am i
```
then when the prompt is being [cleaned up](), if the phrases "from", "you" and "am i" are found they will be deleted from the prompt. Eliminated stopwords can also reduce the cost of processing by reducing the number of tokens that OpenAI needs to process, however eliminated critical words and phrases by mistake can lead to incorrect value extraction.



## Repo Walkthrough

_coming soon_
