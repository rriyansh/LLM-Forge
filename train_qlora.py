import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

# ---------------------------------------------------------
# 1. Config
# ---------------------------------------------------------
MODEL_ID = "meta-llama/Meta-Llama-3-8B"  
DATASET_PATH = "data/train.jsonl"
OUTPUT_DIR = "./llm-forge-checkpoints"
WANDB_PROJECT = "llm-forge-basic"

# ---------------------------------------------------------
# 2. 4-bit Quantization Config (QLoRA ka core)
# ---------------------------------------------------------
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",              # NormalFloat4 — recommended
    bnb_4bit_compute_dtype=torch.bfloat16,  # Stability ke liye
    bnb_4bit_use_double_quant=True,         # Nested quantization, aur memory bachta hai
)

# ---------------------------------------------------------
# 3. Tokenizer & Model Load
# ---------------------------------------------------------
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
tokenizer.pad_token = tokenizer.eos_token  # Llama models mein pad token nahi hota

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

model = prepare_model_for_kbit_training(model)

# ---------------------------------------------------------
# 4. LoRA Config (PEFT)
# ---------------------------------------------------------
peft_config = LoraConfig(
    r=16,                           # Rank — 8, 16, 32 common hain
    lora_alpha=32,                  # Scaling factor
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],  # Llama/Mistral ke liye
)

# ---------------------------------------------------------
# 5. Dataset Load
# ---------------------------------------------------------
dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

# ---------------------------------------------------------
# 6. Training Arguments (W&B logging included)
# ---------------------------------------------------------
sft_config = SFTConfig(
    output_dir=OUTPUT_DIR,
    num_train_epochs=2,
    per_device_train_batch_size=2,       
    gradient_accumulation_steps=8,       
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    bf16=True,
    logging_steps=10,
    save_strategy="epoch",
    max_seq_length=2048,                 
    packing=True,                        
    report_to="wandb",                  
    run_name="llama3-8b-qlora-basic",
)

# ---------------------------------------------------------
# 7. Trainer & Train
# ---------------------------------------------------------
trainer = SFTTrainer(
    model=model,
    args=sft_config,
    train_dataset=dataset,
    peft_config=peft_config,
    processing_class=tokenizer,
)

trainer.train()
trainer.save_model(f"{OUTPUT_DIR}/final")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/final")
