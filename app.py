from flask import Flask, render_template, request, redirect, abort
from os.path import exists
import typing
import hashlib
import sys
import requests
import ipaddress

app = Flask(__name__)

URLS_FILE = open("./urls.txt", "a+")
URLS_FILE.seek(0)
URLS = dict()  # improve this
CONFIG = dict()


def check_for_config():
    if not exists("./.config"):
        CONFIG_FILE = open(".config", "a+")
        CONFIG_FILE.write("""base_url = http://127.0.0.1
host = 0.0.0.0
port = 80
debug = false
        """)
        print(CONFIG_FILE.read())
    else:
        CONFIG_FILE = open(".config", "r")
    return CONFIG_FILE


def parse_config():
    f = check_for_config()
    f.seek(0)
    line_idx = 1
    try:
        for line in f.readlines():
            if len(line.rstrip()) == 0:
                line_idx += 1
                continue
            (key, val) = line.replace(" ", "").split("=")
            val = val.rstrip()

            # checks for invalid values
            if key == 'port' and not val.isdigit():
                print("[WARNING] Port number is not a number, defaulting to port 80")
                val = "80"

            if key == 'host':
                try:
                    ipaddress.ip_address(val)
                except ValueError:
                    print("[WARNING] Host is not a valid IP address, defaulting to 0.0.0.0")
                    val = "0.0.0.0"

            if key == 'debug' and val.lower() != "true" and val.lower() != 'false':
                print("[WARNING] Debug isn't true nor false, defaulting to false")
                val = "false"

            CONFIG[key] = val
            line_idx += 1
    except ValueError:
        print(f"[ERROR] Error in config file, line {line_idx}")
        pass


def parse_urls_file(f: typing.TextIO):
    """
    parses URLs file at the start of the program
    """
    line_idx = 1
    try:
        for line in f.readlines():
            if len(line.rstrip()) == 0:
                line_idx += 1
                continue
            (key, val) = line.split(" ")
            if len(key) != 5:
                print(f"[WARNING] Key {key} in line {line_idx} ignored: Wrong length (not 5)")
                continue
            val = val.rstrip()
            URLS[key] = val
            line_idx += 1
    except ValueError:
        print(f"[ERROR] There is something wrong in the URLs file in line {line_idx}")
        sys.exit(1)


def is_valid_url(url: str):
    """
    checks if the url actually exists
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = f"http://{url}"

    try:
        r = requests.head(url)  # only gets headers
    except:
        """ 
        when trying with certain SSTI payload, it throws an exception when it's supposed to catch the error 
        (requests.exceptions.ConnectionError), so it's better to do bare except (goes against PEP8)
        """
        return render_template("not_valid.html")

    if r.status_code >= 400:
        return render_template("not_valid.html")
    else:
        return create_shortlink(url)


def url_exists_in_file(hashed_url: str, url: str):
    """
    checks if the URL is in the file to avoid duplicated entries
    """
    try:
        URLS[hashed_url]
    except KeyError:
        URLS[hashed_url] = url
        URLS_FILE.write(f"{hashed_url} {url}\n")
    return render_template("created_url.html", BASE=CONFIG['base_url'], hashed=hashed_url)


def create_shortlink(url: str):
    """
    hashes the URL using sha256
    takes the 5 first characters
    returns a template
    """
    hashed_url = hashlib.sha256(url.encode()).hexdigest()[0:5]
    return url_exists_in_file(hashed_url, url)


@app.route("/", methods=['GET'])
def front_page():

    return render_template("index.html")


@app.route("/create_url", methods=['POST'])
def create_url():
    """
    get the URL and do checks
    """
    url = request.form['url']
    return is_valid_url(url)


@app.route("/<string:short_url>")
def redir(short_url: str):
    if short_url in URLS:
        return redirect(URLS[short_url])
    else:
        abort(404)


if __name__ == '__main__':
    parse_urls_file(URLS_FILE)
    parse_config()
    app.run(host=CONFIG['host'],
            port=CONFIG['port'],
            debug=True if CONFIG['debug'].lower() == "true" else False if CONFIG['debug'].lower() == "false" else None)
