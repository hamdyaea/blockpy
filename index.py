#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: hamdy.aea@protonmail.com
# SPDX-License-Identifier: GPL-3.0-or-later
"""Educational in-memory proof-of-work blockchain; not a cryptocurrency."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from threading import Lock

from flask import Flask, abort, redirect, render_template, request, url_for


class Blockchain:
    def __init__(self, difficulty: int = 4):
        if not 1 <= difficulty <= 5:
            raise ValueError("Difficulty must be 1..5")
        self.difficulty = difficulty
        self.chain = []
        self.lock = Lock()
        self.create_block(proof=1, previous_hash="0")

    def create_block(self, proof: int, previous_hash: str):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "proof": proof,
            "previous_hash": previous_hash,
        }
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block):
        return sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def valid_proof(self, previous: int, current: int) -> bool:
        digest = sha256(str(current**2 - previous**2).encode()).hexdigest()
        return digest.startswith("0" * self.difficulty)

    def proof_of_work(self, previous_proof: int) -> int:
        for candidate in range(1, 2_000_001):
            if self.valid_proof(previous_proof, candidate):
                return candidate
        raise RuntimeError("Proof-of-work limit exceeded")

    def mine(self):
        with self.lock:
            previous = self.chain[-1]
            proof = self.proof_of_work(previous["proof"])
            return self.create_block(proof, self.hash(previous))

    def is_chain_valid(self, chain=None):
        chain = self.chain if chain is None else chain
        if not chain or chain[0]["previous_hash"] != "0" or chain[0]["proof"] != 1:
            return False
        for previous, current in zip(chain, chain[1:]):
            if current.get("previous_hash") != self.hash(previous):
                return False
            if not self.valid_proof(previous["proof"], current["proof"]):
                return False
        return True


def create_app(blockchain=None):
    app = Flask(__name__)
    chain = blockchain if blockchain is not None else Blockchain()
    app.config["BLOCKCHAIN"] = chain

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            if "action1" in request.form:
                return mine_block()
            if "action2" in request.form:
                return redirect(url_for("get_chain"), code=303)
            if "action3" in request.form:
                return redirect(url_for("is_valid"), code=303)
        return render_template("index.html", form=None)

    @app.route("/mine_block", methods=["GET", "POST"])
    def mine_block():
        if request.method == "GET":
            return redirect(url_for("index"), code=303)
        # This is intentionally an educational in-memory operation. Public
        # deployments should add authentication and rate limits before use.
        block = chain.mine()
        return render_template("block.html", block={
            "message": "Educational block mined (no real coins)", **block
        })

    @app.get("/get_chain")
    def get_chain():
        return render_template("chain.html", chain={
            "chain": list(chain.chain), "length": len(chain.chain)
        })

    @app.get("/is_valid")
    def is_valid():
        return render_template("validity.html", valid={
            "message": "The Blockchain is valid." if chain.is_chain_valid()
            else "The Blockchain is not valid."
        })

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
