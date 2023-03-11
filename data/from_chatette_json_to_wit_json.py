# read a json from file from chatette format and convert it to wit.ai compoatible format
import json
from pprint import pprint
import sys
import os

# check if input file and output file are provided
if len(sys.argv) < 3:
    print(f"Usage: python {sys.argv[0]} <input_file> <output_file>")
    sys.exit(1)
input_file = sys.argv[1]
# if input_file does not exist exit with error
if not os.path.isfile(input_file):
    print(f"Error: {input_file} does not exist")
    sys.exit(1)
output_file = sys.argv[2]
# check if file already exists
if os.path.isfile(output_file):
    print(f"Error: {output_file} already exists")
    sys.exit(1)
# check if folder alredy exists
if os.path.isdir(output_file):
    print(f"Error: {output_file} already exists")
    sys.exit(1)

file = json.loads(open(input_file).read())


# remove the rasa indentation
examples = file["rasa_nlu_data"]["common_examples"]
# i have the list of dictionaries

# save the body of the entity in the dictionary
for idx, example in enumerate(examples):
    for entity in example["entities"]:
        entity["body"] = example["text"][entity["start"] : entity["end"]]
        entity["entity"] = entity["entity"] + ":" + entity["entity"]
        entity["entities"] = []
    example["traits"] = []

if len(examples) > 100:
    print(
        "Warning: wit.ai limit is 100 examples per file, splitting the file in multiple files"
    )
    # make directory
    os.mkdir(output_file)
    # get the base path
    base = os.path.join(os.path.split(output_file)[0], output_file)
    # limit to 100 examples for each file in order to avoid wit.ai error
    list_examples = [examples[i : i + 100] for i in range(0, len(examples), 100)]
    # save the file
    print(len(examples))
    for idx, example in enumerate(list_examples):
        with open(os.path.join(base, str(idx)) + ".json", "w") as f:
            f.write(json.dumps(example, indent=4))
else:
    with open(output_file, "w") as f:
        f.write(json.dumps(examples, indent=4))
