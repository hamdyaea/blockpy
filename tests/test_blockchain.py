#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: hamdy.aea@protonmail.com
# SPDX-License-Identifier: GPL-3.0-or-later
import unittest
from index import Blockchain, create_app

class BlockchainTests(unittest.TestCase):
    def setUp(self):
        self.chain = Blockchain(difficulty=2)
        self.app = create_app(self.chain)
        self.app.testing = True
        self.client = self.app.test_client()

    def test_genesis_and_validity(self):
        self.assertEqual(len(self.chain.chain), 1)
        self.assertTrue(self.chain.is_chain_valid())

    def test_mining_produces_valid_chain(self):
        self.chain.mine()
        self.assertEqual(len(self.chain.chain), 2)
        self.assertTrue(self.chain.is_chain_valid())

    def test_detect_tampered_block(self):
        self.chain.mine()
        self.chain.chain[1]['proof'] += 1
        self.assertFalse(self.chain.is_chain_valid())

    def test_get_never_mines(self):
        self.assertEqual(self.client.get('/mine_block').status_code, 303)
        self.assertEqual(len(self.chain.chain), 1)

    def test_form_post_mines_once(self):
        result = self.client.post('/', data={'action1': 'Mine'})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(self.chain.chain), 2)

    def test_chain_and_validity_views(self):
        self.assertEqual(self.client.get('/get_chain').status_code, 200)
        self.assertEqual(self.client.get('/is_valid').status_code, 200)

if __name__ == '__main__':
    unittest.main()
