# BlockPy — Educational Blockchain Demonstration

Developer: Hamdy Abou El Anein
Contact: hamdy.aea@protonmail.com
License: GNU GPL v3 (see LICENSE).

A small Flask demonstration of blockchain linking and proof-of-work.
**This is not a cryptocurrency, secure consensus system or persistent ledger.**
Each application process maintains its own independent in-memory chain;
serverless platforms may restart processes and reset the chain.

## Security changes

The old public GET route `/mine_block` performed an unbounded
proof-of-work loop. It could be repeatedly requested by a crawler or
third party and consume server CPU.

The modern version requires **POST** and disables mining by default.
Enable the CPU-intensive demo only on a trusted local development machine:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
BLOCKPY_ALLOW_MINING=1 python index.py
```

Open http://127.0.0.1:5000. The proof-of-work loop has an upper bound of
200,000 attempts; reaching it returns HTTP 503 rather than looping forever.
The demo includes a JSON `/health` endpoint and Flask app-factory tests.

**Do not enable public mining** without real authentication, rate limiting
and a persistent shared ledger. A POST method alone does not protect a
public service from abuse. The original deployed Vercel site has **not**
been changed or redeployed during this modernization.

The previous version is preserved in Git branch `old`.
