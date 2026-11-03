#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: hamdy.aea@protonmail.com
# SPDX-License-Identifier: GPL-3.0-or-later
"""Offline Flask and blockchain tests; no public mining requests."""
from index import Blockchain, create_app


def test_home_and_health():
    client = create_app().test_client()
    assert client.get("/").status_code == 200
    assert client.get("/health").json == {"status": "ok"}


def test_mining_is_disabled_by_default():
    client = create_app(allow_mining=False).test_client()
    assert client.post("/mine_block").status_code == 403
    assert client.post("/", data={"action1": "Mine"}).status_code == 403
    assert client.get("/mine_block").status_code == 405


def test_mining_with_low_difficulty():
    app = create_app(allow_mining=True, difficulty=1)
    client = app.test_client()
    assert client.post("/", data={"action1": "Mine"}).status_code == 200
    chain = app.extensions["blockchain_demo"]
    assert len(chain.chain) == 2
    assert chain.is_chain_valid()
    chain.chain[-1]["proof"] = -1
    assert not chain.is_chain_valid()


def test_pow_attempt_limit():
    chain = Blockchain(difficulty=4)
    try:
        chain.proof_of_work(1, max_attempts=1)
    except TimeoutError:
        pass
    else:
        raise AssertionError("Expected bounded proof-of-work failure")


def test_app_state_is_not_shared_between_factories():
    a = create_app(allow_mining=True, difficulty=1)
    b = create_app(allow_mining=True, difficulty=1)
    a.test_client().post("/mine_block")
    assert len(a.extensions["blockchain_demo"].chain) == 2
    assert len(b.extensions["blockchain_demo"].chain) == 1
