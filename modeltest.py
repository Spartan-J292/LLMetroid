from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load your custom GPT-2
model_name = "./gpt2-finetuned"  # or the huggingface name
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

while True:
    user_input = input("\nYou: ")

    input_ids = tokenizer.encode(user_input, return_tensors='pt')
    output = model.generate(
        input_ids,
        max_length=200,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id
    )

    reply = tokenizer.decode(output[0], skip_special_tokens=True)
    print("\nLLM:", reply)
