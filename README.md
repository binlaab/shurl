# Shurl

Shurl is a simple URL shortener written Python and relies in <a href="https://flask.palletsprojects.com/en/2.2.x/"> Flask</a>. <br>

### Usage
1. Install needed packages:
    `pip install -r requirements.txt`
2. Run the app:
   `python ./app.py`

By default, the app will run in `http://127.0.0.1:80`, base URL will be `http://127.0.0.1` and debug will be turned off.

### Configuration
The app creates a file called `.config` in the app's directory with the default values. The configuration parameters are the following:
* `host`: Address where the app will listen. Defaults to 0.0.0.0 (all interfaces)
* `port`: Port where the app is served. Defaults to port 80.
* `base_url`: The base URL for shortened URLs. Defaults to `http://127.0.0.1`. 
* `debug`: Enable debug mode. Defaults to False.

Invalid parameters will default to the values above and trigger a warning.

This file gets parsed to a dict at the start of the app. In order to apply changes to the configuration, the app must be
restarted.

### How URL shortening works
It takes the 5 first characters of the SHA256 of the URL, and stores it in a file called `urls.txt`, which is located
in the app's directory. The URLs file format is the following:
```
<key> <url>
```
Where `key` is the 5 first characters of the SHA256 hash and `url` is obviously, the URL. This file gets parsed at the
start of the app to a dict. When a key is not 5 characters long, it will be ignored.

Feel free to submit any pull requests and/or issues! If you liked it, please give me a star :) 