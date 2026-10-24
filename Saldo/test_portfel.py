"""Regression tests use isolated CSVs; they never edit the user's portfolio."""
import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('saldo', ROOT / 'server.py')
saldo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(saldo)

def purchase():
    return dict(id='buy-1', name='Test Apple', symbol='AAPL', asset='Akcje', kind='buy',
                date='2025-01-01', quantity=10, price=700, current=800)

EVENTS = [dict(date='2025-02-10', paymentDate='2025-02-20', currency='USD', value=0.25, unadjustedValue=0.25)]

class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=ROOT)
        self.data_dir = Path(self.directory.name)
        self.process = None
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def tearDown(self):
        self.stop()
        self.directory.cleanup()

    def start(self, fixture=False):
        if fixture:
            source = f"import server; server.fetch_dividends=lambda *args: {EVENTS!r}; server.main()"
            command = [sys.executable, '-u', '-c', source]
        else:
            command = [sys.executable, '-u', str(ROOT / 'server.py')]
        self.process = subprocess.Popen(command + ['--port', '0', '--data-dir', str(self.data_dir), '--no-browser'],
                                        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                        encoding='utf-8', errors='replace')
        line = self.process.stdout.readline()
        self.assertTrue(line.startswith('Saldo:'), line)
        self.base = line.split()[1]

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.communicate(timeout=10)
            self.process = None

    def request(self, path, method='GET', body=None):
        headers = {'Origin': self.base, 'Content-Type': 'application/json'}
        req = urllib.request.Request(self.base + path, method=method, headers=headers,
                                     data=json.dumps(body).encode() if body is not None else None)
        with self.opener.open(req, timeout=20) as response:
            return json.load(response)

    def test_restart_csv_and_conflict(self):
        self.start()
        data = self.request('/api/portfolio')
        self.assertEqual(data['rows'], [])
        self.request('/api/portfolio', 'PUT', {'rows':[purchase()], 'revision':data['revision']})
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.request('/api/portfolio', 'PUT', {'rows':[], 'revision':data['revision']})
        self.assertEqual(error.exception.code, 409)
        self.stop()
        self.start()
        rows = self.request('/api/portfolio')['rows']
        self.assertEqual(rows[0]['name'], 'Test Apple')
        self.assertEqual(rows[0]['quantity'], 10)
        self.assertEqual(rows[0]['current'], 800)
        with (self.data_dir / 'portfel.csv').open(encoding='utf-8-sig', newline='') as stream:
            self.assertEqual(list(csv.DictReader(stream))[0]['id'], 'buy-1')

    def test_sync_confirm_deduplicate_restart(self):
        self.start(fixture=True)
        data = self.request('/api/portfolio')
        self.request('/api/portfolio', 'PUT', {'rows':[purchase()], 'revision':data['revision']})
        config = self.request('/api/dividends/settings', 'PUT', {'token':'test-secret', 'symbols':{'AAPL':'AAPL.US'}})
        self.assertTrue(config['configured'])
        self.assertNotIn('test-secret', json.dumps(config))
        self.assertEqual(self.request('/api/dividends/sync', 'POST', {'force':True})['added'], 1)
        self.assertEqual(self.request('/api/dividends/sync', 'POST', {'force':True})['added'], 0)
        data = self.request('/api/portfolio')
        pending = [r for r in data['rows'] if r['kind']=='expected_dividend']
        self.assertEqual(len(pending), 1)
        self.assertEqual(float(pending[0]['expected_amount']), 2.5)
        self.assertEqual(pending[0]['price'], 0)
        self.assertEqual(pending[0]['currency'], 'USD')
        self.request('/api/dividends/confirm', 'POST', {'id':pending[0]['id'], 'amount':8.21, 'date':'2025-02-21'})
        with self.assertRaises(urllib.error.HTTPError):
            self.request('/api/dividends/confirm', 'POST', {'id':pending[0]['id'], 'amount':8.21, 'date':'2025-02-21'})
        self.stop()
        self.start(fixture=True)
        self.request('/api/dividends/sync', 'POST', {'force':True})
        data = self.request('/api/portfolio')
        self.assertEqual(len(data['rows']), 2)
        dividend = [r for r in data['rows'] if r['kind']=='dividend'][0]
        self.assertEqual(dividend['price'], 8.21)
        self.assertEqual(dividend['date'], '2025-02-21')
        self.assertEqual(dividend['status'], 'confirmed')
        self.assertTrue(self.request('/api/dividends/settings')['configured'])
        for path in ['/dane/ustawienia.json', '/server.py', '/dane/', '/../server.py']:
            with self.assertRaises(urllib.error.HTTPError):
                self.request(path)

    def test_eligibility_corrections_missing_payment_and_old_csv(self):
        rows = [purchase(), {**purchase(), 'id':'late', 'date':'2025-02-10', 'quantity':5}]
        added, _ = saldo.merge_events(rows, 'AAPL', 'AAPL.US', EVENTS)
        self.assertEqual(added, 1)
        self.assertEqual(rows[-1]['quantity'], 10)
        changed = [{**EVENTS[0], 'paymentDate':None, 'unadjustedValue':0.30}]
        saldo.merge_events(rows, 'AAPL', 'AAPL.US', changed)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[-1]['payment_date'], '')
        self.assertEqual(float(rows[-1]['expected_amount']), 3)
        path = self.data_dir / 'portfel.csv'
        with path.open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=saldo.BASE_FIELDS)
            writer.writeheader()
            writer.writerow(purchase())
        self.start()
        data = self.request('/api/portfolio')
        self.assertEqual(data['rows'][0]['id'], 'buy-1')
        self.request('/api/portfolio','PUT',{'rows':data['rows'],'revision':data['revision']})
        self.stop()
        self.start()
        self.assertEqual(self.request('/api/portfolio')['rows'][0]['quantity'],10)

    def test_missing_key_invalid_write_and_corrupt_csv(self):
        self.start()
        data = self.request('/api/portfolio')
        with self.assertRaises(urllib.error.HTTPError):
            self.request('/api/dividends/sync', 'POST', {'force':True})
        with self.assertRaises(urllib.error.HTTPError):
            self.request('/api/portfolio', 'PUT', {'rows':[{**purchase(), 'price':-1}], 'revision':data['revision']})
        self.assertEqual(self.request('/api/portfolio')['rows'], [])
        self.stop()
        path = self.data_dir / 'portfel.csv'
        path.write_text('broken header\nleave this intact\n', encoding='utf-8')
        self.start()
        with self.assertRaises(urllib.error.HTTPError):
            self.request('/api/portfolio')
        self.assertEqual(path.read_text(encoding='utf-8'), 'broken header\nleave this intact\n')

    def test_history_records_prices_and_survives_restart(self):
        self.start()
        data = self.request('/api/portfolio')
        self.request('/api/portfolio', 'PUT', {'rows':[purchase()], 'revision':data['revision']})
        yesterday = (date.today()-timedelta(days=1)).isoformat()
        with (self.data_dir / 'historia.csv').open('w', encoding='utf-8-sig', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['date','id','unit_price'])
            writer.writeheader()
            writer.writerow({'date':yesterday,'id':'buy-1','unit_price':750})
        history = self.request('/api/history')['prices']
        self.assertEqual(len(history), 2)
        self.assertEqual(history[-1]['unit_price'], 800)
        data = self.request('/api/portfolio')
        data['rows'][0]['current'] = 810
        self.request('/api/portfolio', 'PUT', data)
        history = self.request('/api/history')['prices']
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['unit_price'], 750)
        self.assertEqual(history[-1]['unit_price'], 810)
        self.stop()
        self.start()
        self.assertEqual(self.request('/api/history')['prices'], history)

    def test_bond_offer_parser_and_terms_restart(self):
        catalog = json.loads((ROOT/'obligacje.json').read_text(encoding='utf-8'))
        offer = '<div>Seria: EDO1036 Cena zakupu 100,00 zł Oprocentowanie 5,35% Odsetki</div>'
        result = saldo.parse_bond_offer(offer, catalog)
        self.assertEqual(result[0]['symbol'], 'EDO1036')
        self.assertEqual(result[0]['rate'], 5.35)
        self.assertEqual(result[0]['sale_from'], '2026-10-01')
        with self.assertRaises(ValueError):
            saldo.parse_bond_offer('<html>changed layout</html>', catalog)
        self.start()
        data = self.request('/api/portfolio')
        row = {**purchase(), 'asset':'Obligacje', 'symbol':'EDO1036', 'price':100, 'current':100,
               'bond_terms':json.dumps(result[0], ensure_ascii=False)}
        self.request('/api/portfolio','PUT',{'rows':[row], 'revision':data['revision']})
        self.stop()
        self.start()
        stored = self.request('/api/portfolio')['rows'][0]
        self.assertEqual(json.loads(stored['bond_terms'])['rate'],5.35)
        self.assertEqual(stored['current'],100)

if __name__ == '__main__':
    unittest.main(verbosity=2)
