# # read all yamls in the actions folder
# import yaml
# import os
# import sys


# # merge all yamls into one

# # list all yamls in the given folder
# def list_yaml_files(folder: str) -> list:
#     list_all = list()
#     for root, subdirs, files in os.walk(folder):
#         for file in files:
#             if file.endswith(".yml") or file.endswith(".yaml"):
#                 list_all.append(os.path.join(root, file))
#     return list_all
    
# print(list_yaml_files(sys.argv[1]))

# # load all yamls into one dict
# def load_all_yamls(paths:list[str]) -> dict:
#     dict_all = dict()
#     for file in paths:
#         with open(file, "r") as f:
#             dict_all.update(yaml.safe_load(f))
#     return dict_all

# d=load_all_yamls(list_yaml_files(sys.argv[1]))

# from pprint import pprint

# pprint(d)

# pprint(d["actions"])

# pprint(d["slots"])