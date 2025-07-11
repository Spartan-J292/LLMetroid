import os
# --- SUPER-SILENT LOGGING SETTINGS ---
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["PYTHONWARNINGS"] = "ignore"

import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)
for noisy_logger in [
    "transformers",
    "datasets",
    "torch",
    "TTS",
    "huggingface_hub",
]:
    logging.getLogger(noisy_logger).setLevel(logging.ERROR)

import time
import random
import re
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from TTS.api import TTS  # Coqui TTS
from pydub import AudioSegment
from pydub.playback import play

# === CONFIG ===
MODEL_PATH = "./gpt2-finetuned"
SNAPSHOT_PATH = "./ram_snapshot.txt"
CHECK_INTERVAL = 60  # every 1 min
VOLUME_BOOST_DB = 10  # 🔊 boost
TEMPERATURE = 1.3
USE_NOISE = True  # add seed noise
HISTORY_SIZE = 5   # Avoid repeating recent lines
REROLL_LIMIT = 10  # Try up to 10 rerolls if Samus repeats herself or outputs junk

# === ANTI-REPEAT SETTINGS ===
BANNED_PHRASES = [
    "The X think they can become me. Let them try.",
	"If the lights flicker, I run. If they stay on, I run faster.",
    # Add more lines to ban if needed!
]

def is_bad(line):
    # Hard ban on stuck lines
    for phrase in BANNED_PHRASES:
        if phrase.lower() in line.lower():
            return True
    return False

def is_repeat(line, recent_lines):
    return any(line.strip().lower() == prev.strip().lower() for prev in recent_lines)

def add_to_history(line, recent_lines):
    recent_lines.append(line.strip())
    if len(recent_lines) > HISTORY_SIZE:
        recent_lines.pop(0)

def slice_monologue(monologue):
    # Split into lines, filter each, stop at first sign of junk
    lines = monologue.splitlines()
    cleaned_lines = []
    for line in lines:
        l = line.strip()
        # Skip blank lines
        if not l:
            continue
        # If line looks like a prompt or HUD, STOP
        if re.search(r"\bHP\b|Missile|Room|Boss|0x[0-9A-Fa-f]+|=>|\d{2,3}[\s:]", l, re.IGNORECASE):
            break
        # If line is just a number or short code, skip
        if len(l) < 4:
            continue
        cleaned_lines.append(l)
    return " ".join(cleaned_lines).strip()

def is_junk(monologue):
    # If line is empty, super short, or looks like data/HUD, call it junk
    if not monologue or len(monologue.split()) < 4:
        return True
    if any(tag in monologue for tag in ["HP:", "Missile", "Room", "Boss", "=>"]):
        return True
    if re.match(r"^0x[0-9A-Fa-f]+", monologue):
        return True
    return False

# === LOAD LLM ===
print("[INFO] Loading tokenizer and model...")
tokenizer = GPT2Tokenizer.from_pretrained(MODEL_PATH)
model = GPT2LMHeadModel.from_pretrained(MODEL_PATH)

# === LOAD TTS ===
print("[INFO] Loading Coqui TTS...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False)
tts.to("cuda")  # or "cpu"

print(f"[INFO] Visor log mode active. Checking every {CHECK_INTERVAL} seconds...")

recent_lines = []

while True:
    if not os.path.exists(SNAPSHOT_PATH):
        print(f"[WARN] RAM snapshot not found: {SNAPSHOT_PATH}")
        time.sleep(CHECK_INTERVAL)
        continue

    with open(SNAPSHOT_PATH, "r") as f:
        snapshot = f.read().strip()

    if snapshot == "":
        print("[INFO] Snapshot empty, waiting...")
        time.sleep(CHECK_INTERVAL)
        continue

    attempt = 0
    monologue = ""
    while attempt < REROLL_LIMIT:
        # === Add seed noise ===
        if USE_NOISE:
            noise = f" // seed:{random.randint(0, 9999)}"
        else:
            noise = ""

        prompt = snapshot + noise + " =>"

        print(f"\n[INFO] RAM snapshot: {snapshot}")
        print(f"[INFO] Prompt: {prompt}")

        # === Generate ===
        input_ids = tokenizer.encode(prompt, return_tensors="pt")
        output = model.generate(
            input_ids,
            max_length=len(input_ids[0]) + 50,
            do_sample=True,
            top_k=80,
            top_p=0.92,
            temperature=TEMPERATURE,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.7,
            no_repeat_ngram_size=4,
        )

        # === Decode ===
        generated_full = tokenizer.decode(output[0], skip_special_tokens=True)
        prompt_decoded = tokenizer.decode(input_ids[0], skip_special_tokens=True)

        print("\n=== RAW GENERATED ===")
        print(generated_full)

        if generated_full.startswith(prompt_decoded):
            monologue = generated_full[len(prompt_decoded):].strip()
        else:
            monologue = generated_full.strip()

        monologue = slice_monologue(monologue)
        monologue = monologue.strip()

        print("\n=== SAMUS SAYS ===")
        print(monologue)

        if is_bad(monologue):
            print(f"[WARN] Banned phrase detected, rerolling... ({attempt+1}/{REROLL_LIMIT})")
            attempt += 1
            continue
        if is_repeat(monologue, recent_lines):
            print(f"[WARN] Repeat detected, rerolling... ({attempt+1}/{REROLL_LIMIT})")
            attempt += 1
            continue
        if is_junk(monologue):
            print(f"[WARN] Output looks like junk, rerolling... ({attempt+1}/{REROLL_LIMIT})")
            attempt += 1
            continue
        break

    if attempt >= REROLL_LIMIT:
        monologue = "If I say that again, Adam owes me a drink."

    add_to_history(monologue, recent_lines)

    # === Speak with pydub + boosted volume ===
    print("\n[INFO] Speaking...")
    tts.tts_to_file(
        text=monologue,
        speaker_wav="combined.wav",
        language="en",
        file_path="suit_output.wav"
    )

    sound = AudioSegment.from_file("suit_output.wav", format="wav")
    louder_sound = sound + VOLUME_BOOST_DB
    play(louder_sound)

    print(f"\n[INFO] Sleeping for {CHECK_INTERVAL} seconds...\n")
    time.sleep(CHECK_INTERVAL)
