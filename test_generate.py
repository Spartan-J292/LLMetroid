import os
import logging
import warnings
import sys
import contextlib

# Muzzle all the noisy shit
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TRANSFORMERS_NO_TF"] = "1"
os.environ["XLA_FLAGS"] = "--xla_cpu_use_xla=false"

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)
logging.getLogger("absl").setLevel(logging.ERROR)

warnings.filterwarnings("ignore")

import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Optional: wrap stderr to silence last bits
@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

tokenizer = GPT2Tokenizer.from_pretrained("./gpt2-finetuned")
model = GPT2LMHeadModel.from_pretrained("./gpt2-finetuned")

prompt = "HP: 7 Missiles: 0 Boss: True Room: 0x1A =>"
inputs = tokenizer.encode(prompt, return_tensors="pt")

# Use eos as pad if pad not defined
pad_token_id = tokenizer.pad_token_id or tokenizer.eos_token_id

attention_mask = (inputs != pad_token_id).long()

with suppress_stderr():
    outputs = model.generate(
        inputs,
        attention_mask=attention_mask,
        max_length=50,
        temperature=0.8,
        do_sample=True,
        pad_token_id=pad_token_id
    )

print(tokenizer.decode(outputs[0]))