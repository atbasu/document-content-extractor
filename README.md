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

## Repo Walkthrough

_coming soon_
