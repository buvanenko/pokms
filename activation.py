import subprocess

def install_key(key: str):
    try:
        out = subprocess.check_output(
            "cscript C:\Windows\System32\slmgr.vbs -ipk " + key,
            shell=True,
        )
    except subprocess.CalledProcessError:
        return False
    return True

def install_kms(host: str):
    try:
        out = subprocess.check_output(
            "cscript C:\Windows\System32\slmgr.vbs  -skms " + host, shell=True
        )
        out = subprocess.check_output(
            "cscript C:\Windows\System32\slmgr.vbs  /ato", shell=True
        )
    except subprocess.CalledProcessError:
        return False
    return True

def check_expire():
    out = subprocess.check_output(
        "cscript C:\Windows\System32\slmgr.vbs /xpr",
        shell=True,
        text=True,
        encoding="cp866"
    )
    return str(out).split(' ')[-2]