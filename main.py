import secrets, string
from keywords import KEYWORDS
from test_set import TEST_SET

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
            out += ch          # keep symbols like - and _
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
        fake = randomize(secret)       # no keyword found: scramble everything
    fake_to_real[fake] = secret
    return fake

def restore(text):
    for fake, real in fake_to_real.items():
        text = text.replace(fake, real)
    return text


if __name__ == '__main__':
    for secret in TEST_SET:
        print(f'{secret}: {sanitize(secret)}')