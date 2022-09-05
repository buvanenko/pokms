import requests

def get():
    hosts = requests.get('https://raw.githubusercontent.com/buvanenko/online-kms/main/hosts').text.split("\n")
    keys = requests.get('https://raw.githubusercontent.com/buvanenko/online-kms/main/keys.json').json()
    return hosts, keys