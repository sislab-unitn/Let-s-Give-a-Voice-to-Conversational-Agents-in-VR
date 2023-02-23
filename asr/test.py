import speechbrain
import torch
from torch.utils.data import DataLoader
import datasets
from datasets import load_dataset
import time
from torchmetrics import WordErrorRate
import wandb
from speechbrain.pretrained import EncoderDecoderASR


device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")


asr_model_names = [
                    'asr-crdnn-rnnlm-librispeech',
                   'asr-wav2vec2-commonvoice-en',
                    'asr-wav2vec2-librispeech',
                    'asr-transformer-switchboard',
                    'asr-crdnn-transformerlm-librispeech',
                    'asr-wav2vec2-switchboard',
                    'asr-crdnn-switchboard',
                    'asr-conformersmall-transformerlm-librispeech'
                    ]

datasets_names = [
                "ami","common_voice","earnings22","gigaspeech","librispeech","spgispeech","tedlium","voxpopuli"
                  ]
dataset_splits = [
                  "clean",
                  "other"
                  ]

tot = 0
for name in datasets_names:
    for split in dataset_splits:
        dataset = load_dataset("esb/diagnostic-dataset", name , split=split)
        tot += len(dataset)
        
total = tot*len(asr_model_names)

print(f"Total number of samples: {total}")


def collate(batch):

    tensors = [torch.tensor(b['audio']['array']).reshape(-1) for b in batch]
    sizes = [t.shape[0] for t in tensors]
    sizes = torch.tensor(sizes)
    sizes = sizes/torch.max(sizes)
    tensors = torch.nn.utils.rnn.pad_sequence(tensors, batch_first=True, padding_value=0)
    ground_truths = [b['norm_transcript'] for b in batch]
    token_counts = [len(b['norm_transcript'].split(' ')) for b in batch]
    return tensors,ground_truths,sizes, token_counts

# model_name = asr_model_names[0]
# asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/"+model_name, savedir="pretrained_models/"+model_name,run_opts={"device":"cpu"})
# opt_mod = torch.compile(asr_model)
# data_loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=8, collate_fn=collate)
# for batch,ground_truths,sizes in data_loader:
#     prediction, t = opt_mod.transcribe_batch(batch,sizes)
#     import pdb; pdb.set_trace()

for model_name in asr_model_names:
    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/"+model_name, savedir="pretrained_models/"+model_name,run_opts={"device":device})
    opt_mod = torch.compile(asr_model)
    for name in datasets_names:
        for split in dataset_splits:
            # start a new wandb run to track this script
            wandb.init(
                # set the wandb project where this run will be logged
                project="ASR WER Test SSH",
                name = model_name+"_"+name+"_"+split,
                # track hyperparameters and run metadata
                config={
                "architecture": model_name,
                "dataset": name,
                "split": split
                }
            )
            dataset = load_dataset("esb/diagnostic-dataset", name , split=split)
            predictions = []
            ground_truths = []
            counter = 0
            token_counts = 0
            wer = WordErrorRate()
            
            data_loader = DataLoader(dataset, batch_size=8, shuffle=False, num_workers=8, collate_fn=collate)
            
            timer = time.time()
            
            for batch,ground_truth,sizes,token_count in data_loader:
                batch.to(device)
                sizes.to(device)
                prediction, _  = opt_mod.transcribe_batch(batch,sizes)
                token_counts += sum(token_count)
                predictions += prediction
                ground_truths += ground_truth
                break
                
            timer = time.time() - timer
            
            average_time = timer/len(dataset)
            current = wer(predictions, ground_truths)
            wandb.log({"WER": current})
            wandb.log({"Tokens per second": token_counts/timer})
            wandb.log({"Average time per sample": average_time})
            wandb.log({"Total time": timer})
            wandb.log({"Total samples": len(dataset)})
            wandb.log({"Total tokens": token_counts})
            wandb.finish()