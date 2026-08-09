# GPTQ Quantization Template (4-bit)

Use GPTQ to quantize large LLMs for GPU inference.

---

## 1. Calibration Data

calibration:
num_samples: 256
max_seq_length: 2048
dataset_path: "<path/to/calibration/text>"

---

## 2. GPTQ Settings

gptq:
bits: 4
damp_percent: 0.01
desc_act: true
blocksize: 128
groupsize: 128
act_order: true

---

## 3. Output

output:
quantized_model_path: "<output_dir>"

---

## 4. Validation Checklist

- [ ] Quantized model loads  
- [ ] Per-layer error acceptable  
- [ ] Output quality tested on eval set
