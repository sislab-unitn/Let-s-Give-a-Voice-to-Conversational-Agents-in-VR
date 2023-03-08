from datasets import load_dataset

esb_diagnostic_common_voice = load_dataset("esb/diagnostic-dataset", "common_voice")

for example in esb_diagnostic_common_voice:
    print(example)