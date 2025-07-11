# LLMetroid


### Ever wish Samus Aran would narrate her own existential dread while exploring? LLMetroid makes it happen. This is a proof-of-concept that uses a fine-tuned LLM and emulator Lua scripting to bring inner monologue to Metroid.

# What Is This?
### LLMetroid hooks a custom-trained GPT-2 model to your Metroid emulator (tested on BizHawk & mGBA).
### The Lua script grabs Samus’s energy, missile count, and room info and feeds it to the LLM, generating real-time Samus commentary.

## Setup Guide
# 1. Clone This Repo
   
git clone https://github.com/Spartan-J292/LLMetroid.git

cd LLMetroid

# 2. You need two venvs:
One for training the model
One for running the TTS/voice stuff

## Training Virtual Enviroment Setup

### Training Venv
python -m venv train_venv
source train_venv/bin/activate   # Linux/macOS
.\train_venv\Scripts\activate   # Windows
pip install -r requirements-train.txt

### Voice venv
python -m venv voice_venv

### Linux/MacOS
source voice_venv/bin/activate

### Windows
.\voice_venv\Scripts\activate

pip install -r requirements-voice.txt

# 3. Train or Load Your Model
To train your own Samus-brain, run:


python train_gp2.py
This will create a gpt2-finetuned directory (used by suit_voice.py).

# 4. Set Up Your Emulator
Use an emulator that supports Lua scripting (tested with BizHawk & mGBA).

Open mgba_ram_watch.lua (or whatever Lua script you use for RAM scraping) in the emulator.

# 5. Run the Samus Voice
Activate your voice venv:

### Linux/macOS
source voice_venv/bin/activate

### Windows
.\voice_venv\Scripts\activate        

Start the commentary:
python suit_voice.py

# 6. Demo
Check out suit_output.wav for a sample of what the voice output sounds like.

Notes
NO ROMS/NO EMULATOR BUNDLED – get your own!

Fine-tune the Lua script for your favorite Metroid if needed.

This is a proof-of-concept, not a polished product.

Expect jank, but also fun.

Credits
Spartan-J292

Powered by curiosity, caffeine, and ChatGPT heckling
