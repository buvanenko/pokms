import requests

ver = "0.4.0"

def get():
    hosts = requests.get('https://raw.githubusercontent.com/buvanenko/online-kms/main/hosts').text.split("\n")
    keys = requests.get('https://raw.githubusercontent.com/buvanenko/online-kms/main/keys.json').json()
    version = requests.get('https://raw.githubusercontent.com/buvanenko/online-kms/main/version.json').json()
    return hosts, keys, version