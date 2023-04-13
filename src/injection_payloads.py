"""Load injection payloads from JSON catalogue."""
import json
import pathlib


def load_payloads(path=None):
    if path is None:
        path = pathlib.Path(__file__).resolve().parent.parent / 'payloads' / 'known_attacks.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


