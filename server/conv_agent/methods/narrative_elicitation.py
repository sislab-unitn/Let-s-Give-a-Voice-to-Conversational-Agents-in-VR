import torch
import transformers

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

import requests


def get_pipeline(config):
    model_name = config["model"]["model_name"]
    lora_weights = config["model"]["lora_weights"]
    device = config["model"]["device"]
    token_id = config["model"]["token_id"]
    dtype = torch.bfloat16

    tokenizer = AutoTokenizer.from_pretrained(model_name, token=token_id)

    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=dtype, device_map=device, token=token_id)

    model.eval()

    history = {"history": ""}
    return model, tokenizer, history


def model_response(pipeline, tokenizer, narrative, history):
    condition = """NARRATIVA:\n{input_text}\n\nDOMANDA:\n"""

    encodings_dict = tokenizer(condition.format(input_text=narrative), return_tensors='pt', return_attention_mask=True)
    
    model_outputs = pipeline.generate(input_ids=encodings_dict['input_ids'].to('cuda'), 
                                   attention_mask =encodings_dict['attention_mask'].to('cuda'),
                                       return_dict_in_generate=True, 
                                       num_return_sequences = 1,
                                       max_new_tokens=128,
                                       do_sample=True,
                                       top_k=10,
                                       eos_token_id=tokenizer.eos_token_id)
    
    model_out = tokenizer.decode(model_outputs.sequences[0]).split('DOMANDA:')[1]

    if '?' in model_out:
        model_out = model_out.split('?')[0] + '?'
    elif '.' in model_out:
        model_out = model_out.split('.')[0] + '.'
    
    return model_out


def get_scripted(message, url):
    URL = url + '&message=' + message
    print(URL)

    # sending get request and saving the response as response object
    r = requests.get(url = URL)

    # extracting data in json format
    data = r.json()

    if data['response']:
        return data['response']
    else:
        return 'error'

