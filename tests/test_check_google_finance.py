import sys
import os
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# provide minimal stubs for external dependencies when they are missing
if 'requests' not in sys.modules:
    sys.modules['requests'] = types.ModuleType('requests')
if 'bs4' not in sys.modules:
    bs4_stub = types.ModuleType('bs4')
    bs4_stub.BeautifulSoup = object
    sys.modules['bs4'] = bs4_stub

import check_google_finance as cg


def test_check_ticker_sends_email(monkeypatch):
    monkeypatch.setattr(cg, 'fetch_prices', lambda ticker: (100.0, 110.0))
    called = {}

    def fake_send_email(subject, body):
        called['subject'] = subject
        called['body'] = body

    monkeypatch.setattr(cg, 'send_email', fake_send_email)
    cg.check_ticker('TEST:NASDAQ', threshold=5.0)
    assert 'subject' in called and 'body' in called
