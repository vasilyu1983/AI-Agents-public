# Fine-Tuning Configuration Template

A reproducible config for SFT, instruction tuning, or LoRA.

---

## 1. Model Settings

base_model: <model_name>
tokenizer: <model_tokenizer>
max_seq_length: <length>
gradient_checkpointing: true/false

---

## 2. Training Parameters

learning_rate: 1e-5
batch_size: <value>
num_epochs: <value>
warmup_steps: <value>
seed: 42
eval_steps: <value>
save_steps: <value>

---

## 3. LoRA (Optional)

lora:
enable: true
r: 8
alpha: 16
dropout: 0.05
target_modules: ["q_proj", "v_proj"]

---

## 4. Data

train_file: "<path/to/train.jsonl>"
validation_file: "<path/to/validation.jsonl>"
format: "instruction" | "chat" | "transform"

---

## 5. Output

output_dir: "<path/to/output>"
save_total_limit: 3
log_to_file: true

---

## 6. Safety

- Validate dataset before training  
- Remove harmful content  
- Include refusal samples  
