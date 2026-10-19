# Secret Format Preserver

Swaps real secrets for fake ones that look the same, so you can send prompts to an external LLM without leaking the real values. After the LLM answers, you put the real secrets back.

```
sk_live_12342        ->  sk_live_80917
ghp_Ab12Cd34Ef56...  ->  ghp_Xy98Zt76Qw54...
```

## How it works

1. You pass in a value you already know is a secret.
2. It looks for a known keyword (like `sk_live_` or `AKIA`) anywhere in the value. The longest matching keyword wins.
3. The keyword stays. Every other character is replaced with a random one of the same type: digit for digit, uppercase for uppercase, lowercase for lowercase. Symbols (`-`, `_`, `.`) stay.
4. If no keyword is found, the whole value is scrambled.
5. The fake-to-real pairs are remembered, so `restore()` can undo the swap in the LLM's answer.

## Files

| File | What it does |
|---|---|
| `keywords.py` | A set of keywords, based on the default [Gitleaks](https://github.com/gitleaks/gitleaks) rules (MIT license) |
| `sanitize.py` | `sanitize()` and `restore()` |

## Code

```python
import secrets, string
from keywords import KEYWORDS

WORDS = sorted({k.lower() for k in KEYWORDS}, key=len, reverse=True)
fake_to_real = {}

def randomize(text):
    out = ""
    for ch in text:
        if ch.isdigit():
            out += secrets.choice(string.digits)
        elif ch.isupper():
            out += secrets.choice(string.ascii_uppercase)
        elif ch.islower():
            out += secrets.choice(string.ascii_lowercase)
        else:
            out += ch
    return out

def sanitize(secret):
    lower = secret.lower()
    for word in WORDS:
        i = lower.find(word)
        if i != -1:
            j = i + len(word)
            fake = randomize(secret[:i]) + secret[i:j] + randomize(secret[j:])
            break
    else:
        fake = randomize(secret)
    fake_to_real[fake] = secret
    return fake

def restore(text):
    for fake, real in fake_to_real.items():
        text = text.replace(fake, real)
    return text
```

## Usage

```python
safe = sanitize("sk_live_12342")        # send this to the LLM
answer = "Your key sk_live_80917 looks fine."
print(restore(answer))                  # real secret is back
```

## Limits

- **Detection is separate.** This only changes values you give it. A secret your detector misses goes out unchanged.
- **Keep `fake_to_real` private.** It holds your real secrets. Never log or print it.
- **Formats are close, not exact.** Tokens that allow only certain characters (hex tokens, AWS keys) can get a fake with characters a real one would never have. Fine for an LLM, but not for strict validators.
- **Checksums are not recomputed.** Formats with a built-in checksum will fail validation.
- **Same secret twice gives two fakes.** `restore()` still handles both.
- **Short keywords** (like `sk` or `s.`) can match by accident. The only effect is a few unscrambled characters.