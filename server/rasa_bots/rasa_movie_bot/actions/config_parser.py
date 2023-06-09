import argparse
import os
import pathlib
import sys

try:
    import tomllib
except ImportError:
    import toml as tomllib


def config_parser(argv: str = None, current_path: str = None) -> dict:
    parser = argparse.ArgumentParser(
        prog="Server", description="Server", epilog="Enjoy the program! :)"
    )  # positional argument
    parser.add_argument("-c", "--config", required=False)  # option that takes a value
    args, unknown = parser.parse_known_args(argv)

    # check if config file path is provided and valid
    if args.config:
        # validate config file path
        if os.path.exists(args.config):
            config_path = args.config
        else:
            print(f"'{args.config}' is not a file or does not exist")
            sys.exit(1)
    else:
        if current_path is None:
            current_path = pathlib.Path(__file__).parent.absolute()
        else:
            current_path = os.path.abspath(current_path)
        # find config file in the current directory
        config_toml = list(filter(lambda x: x.endswith(".toml"), os.listdir(current_path)))
        if len(config_toml) == 0:
            print("No config file found in the server directory")
            sys.exit(1)
        config_path = os.path.join(current_path, config_toml[0])
        
    print(f"Using config at :{config_path}")
    # read config file
    with open(config_path, mode="r") as f:
        config = tomllib.loads(f.read())
    return config
