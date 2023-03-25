# import subprocess

# subprocess.run("cd asr/ && python asr_server.py", shell=True)
# subprocess.run("cd tts/ && python tts_server.py", shell=True)

from multiprocessing import Process
import os
import sys

from src.config_parser import config_parser


def run_command(path: str, args: str = ""):
    print(f"Running {path} {args}")
    os.system(f"{path} {args}")


if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # print(sys.path)
    config = config_parser(sys.argv[1:])
    if config["server"]["autostart_tts"]:
        p_asr = Process(
            target=run_command,
            args=(
                "python " + config["server"]["asr_path"],
                config["server"]["asr_args"],
            ),
        )
    if config["server"]["autostart_asr"]:
        p_tts = Process(
            target=run_command,
            args=(
                "python " + config["server"]["tts_path"],
                config["server"]["tts_args"],
            ),
        )
    if config["server"]["autostart_rasa"]:
        command = f'cd {config["server"]["rasa_path"]} && rasa shell'
        p_rasa = Process(
            target=run_command, args=(command, config["server"]["rasa_args"])
        )
    if config["server"]["autostart_rasa_actions"]:
        command = f'cd {config["server"]["rasa_path"]} && rasa run actions'
        p_rasa_actions = Process(
            target=run_command,
            args=(config["server"]["rasa_path"], config["server"]["rasa_actions_args"]),
        )

    p_server = Process(target=run_command, args=("python server.py", ""))

    try:
        p_asr.start()
    except NameError:
        pass
    try:
        p_tts.start()
    except NameError:
        pass
    try:
        p_rasa.start()
    except NameError:
        pass
    try:
        p_rasa_actions.start()
    except NameError:
        pass

    p_server.start()

    try:
        p_asr.join()
    except NameError:
        pass
    try:
        p_tts.join()
    except NameError:
        pass
    try:
        p_rasa.join()
    except NameError:
        pass
    try:
        p_rasa_actions.join()
    except NameError:
        pass

    p_server.join()
