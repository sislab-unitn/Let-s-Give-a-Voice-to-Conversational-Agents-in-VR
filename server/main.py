from multiprocessing import Process
import os
import sys
from subprocess import call
from subprocess import Popen

from src.config_parser import config_parser


def run_command(path: str, args: str = ""):
    print(f"Running {path} {args}")
    os.system(f"{path} {args}")


if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    print(os.path.dirname(os.path.abspath(__file__)))
    config = config_parser(sys.argv[1:])
    if config["server"]["autostart_tts"]:
        tts_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),config["server"]["tts_path"])
        p_tts = Process(target=call, args=(["python", tts_path],), name="tts")
        p_tts.start()
        
    if config["server"]["autostart_asr"]:
        asr_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),config["server"]["asr_path"])
        p_asr = Process(target=call, args=(["python", asr_path],), name="asr")
        p_asr.start()
    bots = []
    # for bot in config["bots"]:
    #     print(bot)
    #     if bot["autostart_rasa"]:
    #         bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),bot["rasa_path"])
    #         p_bot = Process(target=run_command, args=(f"conda init; conda activate {bot['rasa_env']}; python {bot_path}",), name=bot["name"])
    #         p_bot.start()
            # bots.append(p_bot)
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'src/server.py')
    server_path = Process(target=call, args=(["python", server_path],), name="server")
    server_path.start()
    try: 
        p_tts.join()
    except NameError:
        pass
    try: 
        p_asr.join()
    except NameError:
        pass
    for bot in bots:
        bot.join()