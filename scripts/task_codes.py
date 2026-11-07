"""Task codes as shown on the site.

The five original Mind tasks keep their short ids (E, F, M, P, S) in URLs, file names and media
paths. On the page they read E1, F1, M1, P1, S1 so each pairs with its follow-up task (E2 ... S2).
"""
import json
from pathlib import Path

_NAV = json.loads((Path(__file__).resolve().parents[1] / 'data/benchmark-navigation.json').read_text())
_IDS = {c['id'] for s in _NAV for c in s['cases']}


def code(task_id):
    """E -> E1 when E2 exists; every other id is shown as is."""
    return task_id + '1' if task_id + '2' in _IDS else task_id
