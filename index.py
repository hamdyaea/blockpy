#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: hamdy.aea@protonmail.com
# SPDX-License-Identifier: GPL-3.0-or-later
"""Educational in-memory blockchain. Not a real cryptocurrency or consensus protocol."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from threading import RLock

from flask import Flask, abort, redirect, render_template, request, url_for


class Blockchain:
    def __init__(self, difficulty: int = 4):
        if not 1 <= difficulty <= 4:
            raise ValueError("Demo difficulty must be between 1 and 4")
        self.difficulty = difficulty
        self.lock = RLock()
        self.chain = [self._block(1, 1, "0")]

    @staticmethod
    def _block(index: int, proof: int, previous_hash: str) -> dict:
        return {"index": index,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "proof": proof, "previous_hash": previous_hash}

    @staticmethod
    def hash(block: dict) -> str:
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def valid_proof(self, previous: int, candidate: int) -> bool:
        digest = hashlib.sha256(str(candidate**2 - previous**2).encode()).hexdigest()
        return digest.startswith("0" * self.difficulty)

    def proof_of_work(self, previous: int, max_attempts: int = 200_000) -> int:
        # Bound CPU consumption for a public educational web application.
        for candidate in range(1, max_attempts + 1):
            if self.valid_proof(previous, candidate):
                return candidate
        raise TimeoutError("Proof-of-work attempt limit reached")

    def mine(self) -> dict:
        with self.lock:
            previous = self.chain[-1]
            proof = self.proof_of_work(previous["proof"])
            block = self._block(len(self.chain) + 1, proof, self.hash(previous))
            self.chain.append(block)
            return block

    def is_chain_valid(self) -> bool:
        with self.lock:
            if not self.chain or self.chain[0]["previous_hash"] != "0":
                return False
            for previous, current in zip(self.chain, self.chain[1:]):
                if current["index"] != previous["index"] + 1:
                    return False
                if current["previous_hash"] != self.hash(previous):
                    return False
                if not self.valid_proof(previous["proof"], current["proof"]):
                    return False
            return True


def create_app(*, allow_mining: bool | None = None, difficulty: int = 4) -> Flask:
    application = Flask(__name__)
    blockchain = Blockchain(difficulty)
    if allow_mining is None:
        allow_mining = os.environ.get("BLOCKPY_ALLOW_MINING", "0") == "1"
    application.config["ALLOW_MINING"] = allow_mining
    application.extensions["blockchain_demo"] = blockchain

    @application.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            # Keep historical HTML form button names.
            if request.form.get("action1") == "Mine":
                return mine_block()
            if request.form.get("action2") == "Blockchain":
                return redirect(url_for("get_chain"))
            if request.form.get("action3") == "Validity":
                return redirect(url_for("is_valid"))
            return redirect(url_for("index"))
        return render_template("index.html", form=None)

    @application.post("/mine_block")
    def mine_block():
        if not application.config["ALLOW_MINING"]:
            abort(403, description="Mining is disabled by default on public deployments.")
        try:
            block = blockchain.mine()
        except TimeoutError:
            abort(503, description="Proof-of-work limit reached.")
        return render_template("block.html", block={
            "message": "Congratulations, you mined a demonstration block!",
            **block,
        })

    @application.get("/get_chain")
    def get_chain():
        with blockchain.lock:
            chain = {"chain": [dict(block) for block in blockchain.chain],
                     "length": len(blockchain.chain)}
        return render_template("chain.html", chain=chain)

    @application.get("/is_valid")
    def is_valid():
        return render_template("validity.html", valid={
            "message": "The Blockchain is valid." if blockchain.is_chain_valid()
            else "The Blockchain is not valid."
        })

    @application.get("/health")
    def health():
        return {"status": "ok"}

    return application


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
