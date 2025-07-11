import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

from transformers import GPT2Tokenizer, GPT2LMHeadModel, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling

# Load tokenizer and base GPT-2 model
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Prepare dataset
def load_dataset(file_path, tokenizer, block_size=128):  # <-- Your true block_size here
    return TextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=block_size,
    )

dataset = load_dataset("data.txt", tokenizer, block_size=128)

# Collator for batching & masking
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False
)

# Training config — ✅ NO BLOCK_SIZE HERE
training_args = TrainingArguments(
    output_dir="./gpt2-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=750,   # savage imprint, your call
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=3e-5,
    warmup_steps=100,
    logging_steps=10,
    save_steps=50,
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=dataset,
)

# Start training!
trainer.train()

# Save it
trainer.save_model("./gpt2-finetuned")
