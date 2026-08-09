# BPE Tokenizer From Scratch

Reference for building a byte-level BPE tokenizer from first principles, following the minbpe approach.

## Table of Contents

- [Canonical Sources](#canonical-sources)
- [Why Byte-Level](#why-byte-level)
- [Algorithm Overview](#algorithm-overview)
- [Merge Loop](#merge-loop)
- [Encode and Decode](#encode-and-decode)
- [Special Tokens](#special-tokens)
- [Gotchas](#gotchas)

## Canonical Sources

- Karpathy "Let's build the GPT Tokenizer" — https://www.youtube.com/watch?v=zduSFxRajkE
- minbpe — https://github.com/karpathy/minbpe
- GPT-2 tokenizer paper section: "Language Models are Unsupervised Multitask Learners" (Radford et al. 2019)
- tiktoken (OpenAI BPE implementation) — https://github.com/openai/tiktoken

## Why Byte-Level

Standard BPE operates on characters. Byte-level BPE:
- Encodes text as UTF-8 bytes first (256 base tokens, one per byte value 0-255)
- Guarantees the tokenizer can encode ANY Unicode string without unknown tokens
- Sidesteps language-specific preprocessing

Base vocabulary: integers 0-255, each representing one byte.

## Algorithm Overview

```
1. Encode training text as a sequence of byte integers (0-255)
2. Repeat until vocab_size reached:
   a. Count all adjacent pair frequencies in the current token sequence
   b. Find the highest-frequency pair (tie-break: first occurrence)
   c. Add new token ID for this pair (next available int after 255)
   d. Replace all occurrences of the pair in the sequence with the new token
   e. Record the merge rule: (pair) -> new_token_id
3. Save vocab (id -> bytes) and merges (pair -> id)
```

## Merge Loop

```python
def get_stats(ids):
    """Count adjacent pair frequencies."""
    counts = {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts

def merge(ids, pair, idx):
    """Replace all occurrences of pair in ids with idx."""
    new_ids = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i+1] == pair[1]:
            new_ids.append(idx)
            i += 2
        else:
            new_ids.append(ids[i])
            i += 1
    return new_ids

# Training
text_bytes = text.encode('utf-8')
ids = list(text_bytes)  # list of ints in [0, 255]
merges = {}  # (int, int) -> int
vocab = {i: bytes([i]) for i in range(256)}  # id -> bytes

num_merges = vocab_size - 256
for i in range(num_merges):
    stats = get_stats(ids)
    pair = max(stats, key=stats.get)
    new_id = 256 + i
    ids = merge(ids, pair, new_id)
    merges[pair] = new_id
    vocab[new_id] = vocab[pair[0]] + vocab[pair[1]]
```

Key: `vocab[new_id]` is always built from the byte representations of the two merged tokens — this builds up multi-byte sequences correctly.

## Encode and Decode

```python
def encode(text):
    """Encode a string to a list of token IDs."""
    ids = list(text.encode('utf-8'))
    while len(ids) >= 2:
        stats = get_stats(ids)
        # find the earliest (lowest new_id) merge rule that applies
        pair = min(stats, key=lambda p: merges.get(p, float('inf')))
        if pair not in merges:
            break
        ids = merge(ids, pair, merges[pair])
    return ids

def decode(ids):
    """Decode a list of token IDs back to a string."""
    tokens = b''.join(vocab[i] for i in ids)
    return tokens.decode('utf-8', errors='replace')
```

Encode priority: apply merge rules in the order they were learned (lowest merge ID = applied first). This is implemented by picking the pair with minimum `merges[pair]` value.

## Special Tokens

GPT-2 uses `<|endoftext|>` (token ID 50256) as a document separator. Implementation:

```python
# After building the base BPE vocab (IDs 0-50255 for GPT-2's 50k merges)
special_tokens = {'<|endoftext|>': 50256}
# In encode: check for special tokens before byte-level encoding
# In decode: handle special token IDs separately before byte decode
```

minbpe's `RegexTokenizer` also pre-tokenizes with a regex pattern (from GPT-4) to prevent merges across whitespace/punctuation/word boundaries — this is the GPT-2 "pre-tokenization" step.

## Gotchas

- **Off-by-one in merge priority**: encode must apply merges in the order they were learned, not by pair frequency in the current string.
- **No merges across word boundaries**: GPT-2 pre-tokenizes with a regex before BPE. Skipping this produces different tokens from tiktoken.
- **UTF-8 decode errors**: when decoding, some partial token sequences may not be valid UTF-8 — use `errors='replace'` or handle the `UnicodeDecodeError`.
- **Vocab vs merges**: `vocab` maps ID -> bytes (for decode); `merges` maps pair -> ID (for encode). Both are needed; one is not derivable from the other at inference time.
- **Round-trip test**: `assert decode(encode(text)) == text` — run this on a diverse sample including emoji and non-ASCII before trusting the tokenizer.
- **Training corpus size**: BPE quality degrades on very small corpora. Use at least a few MB of text for meaningful merge statistics.
