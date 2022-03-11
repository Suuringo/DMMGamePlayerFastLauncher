import subprocess
import requests
import argparse
import tempfile
import re

requests.packages.urllib3.disable_warnings()

argpar = argparse.ArgumentParser(
    prog="DMMGamePlayerFastLauncher",
    usage="https://github.com/fa0311/DMMGamePlayerFastLauncher",
    description="DMM Game Player Fast Launcher",
)

argpar.add_argument("product_id")
argpar.add_argument("game_path")
arg = argpar.parse_args()

argpar.add_argument("-dgp-path", "--dmmgameplayer-path", default="C:/Program Files/DMMGamePlayer/DMMGamePlayer.exe".format(product_id=arg.product_id))
argpar.add_argument("--game-uri", default="dmmgameplayer://{product_id}/cl/general/{product_id}".format(product_id=arg.product_id))
argpar.add_argument("--temp-path", default="{tempdir}/dmm.log".format(product_id=arg.product_id, tempdir=tempfile.gettempdir().replace("\\","/")))
argpar.add_argument("--kill", default=True)
arg = argpar.parse_args()

headers = {
    "Host": "apidgp-gameplayer.games.dmm.com",
    "Connection": "keep-alive",
    "User-Agent": "DMMGamePlayer5-Win/17.1.2 Electron/17.1.2",
    "Client-App": "DMMGamePlayer5",
    "Client-version": "17.1.2",
}

params = {
    "product_id": arg.product_id,
    "game_type": "GCL",
    "game_os": "win",
    "launch_type": "LIB",
    "mac_address": "00:11:22:33:44:55",
    "hdd_serial": "0000000011111111222222223333333344444444555555556666666677777777",
    "motherboard": "0000000011111111222222223333333344444444555555556666666677777777",
    "user_os": "win"
}

def get_dmm_session():
    process = subprocess.Popen(args="", executable=arg.dmmgameplayer_path, shell=True, stdout=subprocess.PIPE)
    for line in process.stdout:
        text = (line.decode("utf8").strip())
        if 'Header key: "cookie"' in text:
            dmm_session =  re.findall(r'"(.*?)"', text)[1]
            login_session_id = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89aAbB][a-f0-9]{3}-[a-f0-9]{12}', dmm_session)[0]
            login_secure_id = re.search(r'[a-f0-9]{32}', dmm_session)[0]
            if arg.kill:
                process.terminate()
            return login_session_id, login_secure_id

login_session_id, login_secure_id = get_dmm_session()
cookies = {
    "login_session_id": login_session_id,
    "login_secure_id": login_secure_id
}

response = requests.session().post("https://apidgp-gameplayer.games.dmm.com/v5/launch/cl", headers=headers, cookies=cookies, json=params,verify=False)
dmm_args = response.json()["data"]["execute_args"].split(" ")

subprocess.Popen([arg.game_path, dmm_args[0], dmm_args[1]], shell=True)