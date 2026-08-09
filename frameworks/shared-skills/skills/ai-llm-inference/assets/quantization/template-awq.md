# AWQ Quantization Template (Activation-Aware)

AWQ delivers high-quality weight-only quantization with low accuracy loss.

---

## 1. Calibration

calibration_set:
size: 256
source: "<path>"

---

## 2. AWQ Parameters

awq:
alpha: 0.5
clip: true
symmetric: false
quant_group_size: 128

---

## 3. Output

output:
path: "<target_dir>"

---

## 4. Checklist

- [ ] No NaNs after quantization  
- [ ] KV cache tested  
- [ ] Matching tokenizer used  
