# BlockPy — educational proof-of-work blockchain

Developer: Hamdy Abou El Anein
Contact: hamdy.aea@protonmail.com
License: GNU GPL v3 (see LICENSE).

This Flask demonstration shows how an in-memory sequence of blocks, a proof-of-work calculation, and hash-based chain validation work. **It is not a real cryptocurrency and does not mine Bitcoin or Dogecoin.**

## Local setup

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python index.py
```

Open http://127.0.0.1:5000/. The built-in Flask server listens on localhost only.

## Improvements

- Explicit UTC timestamps and a configurable proof-of-work difficulty (1–5 leading hexadecimal zeroes).
- Atomic mining under a thread lock, preventing concurrent requests from corrupting the chain.
- Mining requires POST; GET requests cannot change the blockchain.
- Bounded proof search, basic chain validation and a reusable application factory.
- Six offline tests using Flask's test client, with no network connections.

```sh
python3 -m unittest discover -s tests -v
```

**Deployment warning:** this application is for local demonstrations. The chain is held in process memory and resets on restart. It is not persistent or synchronized across workers. Before deploying publicly, add authentication, CSRF protection, rate limiting, and resource controls for the mining endpoint. A Vercel/serverless deployment cannot guarantee a shared blockchain across requests.

The original version is preserved in the Git branch `old`.
