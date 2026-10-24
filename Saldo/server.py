"""Local-only Saldo: atomic CSV storage and EODHD expected dividends."""
import argparse
import csv
import hashlib
import json
import math
import os
import re
import threading
import urllib.parse
import urllib.request
import uuid
import webbrowser
import calendar
from html.parser import HTMLParser
from datetime import date, datetime, timezone
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'dane' / 'portfel.csv'
BASE_FIELDS = ['id', 'name', 'symbol', 'asset', 'kind', 'date', 'quantity', 'price', 'current']
META_FIELDS = ['event_id', 'status', 'currency', 'ex_date', 'payment_date', 'per_share', 'expected_amount', 'source', 'synced_at', 'bond_terms']
FIELDS = BASE_FIELDS + META_FIELDS
LOCK = threading.RLock()
SYNC_LOCK = threading.Lock()

class Conflict(Exception):
    pass

def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8', newline='') as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

def write_rows(rows):
    import io
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=FIELDS, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    atomic_text(DATA, '\ufeff' + stream.getvalue())

def read_rows():
    if not DATA.exists():
        write_rows([])
    with DATA.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames not in [BASE_FIELDS, FIELDS[:-1], FIELDS]:
            raise ValueError('Nieprawidłowe kolumny pliku CSV. Plik nie został zmieniony.')
        rows = list(reader)
    for row in rows:
        for field in ['quantity', 'price', 'current']:
            row[field] = float(row[field])
        for field in META_FIELDS:
            row.setdefault(field, '')
    validate_rows(rows)
    return rows

def revision():
    return hashlib.sha256(DATA.read_bytes()).hexdigest()


def portfolio_history(rows):
    """Record actual observed lot prices, never infer past prices from today's price."""
    path = DATA.parent / 'historia.csv'
    fields = ['date', 'id', 'unit_price']
    history = []
    if path.exists():
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            if reader.fieldnames != fields:
                raise ValueError('Nieprawidłowy format historii wycen.')
            history = list(reader)
        for item in history:
            day(item['date'])
            item['unit_price'] = float(item['unit_price'])
            if not math.isfinite(item['unit_price']) or item['unit_price'] < 0:
                raise ValueError('Nieprawidłowa wycena historyczna.')
    today = date.today().isoformat()
    history = [item for item in history if item['date'] != today]
    history.extend({'date': today, 'id': row['id'], 'unit_price': row['current']}
                   for row in rows if row['kind'] == 'buy' and row['date'] <= today)
    import io
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields)
    writer.writeheader()
    writer.writerows(history)
    atomic_text(path, '\ufeff' + stream.getvalue())
    return history

def config_path():
    return DATA.parent / 'ustawienia.json'

def read_config():
    path = config_path()
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'token': '', 'symbols': {}, 'checked': {}, 'errors': []}

def write_config(config):
    atomic_text(config_path(), json.dumps(config, ensure_ascii=False, indent=2))

def public_config(config):
    return {'configured': bool(config.get('token')), 'symbols': config.get('symbols', {}), 'checked': config.get('checked', {}), 'errors': config.get('errors', [])}

def day(value):
    return date.fromisoformat(value).isoformat()

def validate_rows(rows):
    if not isinstance(rows, list):
        raise ValueError('Nieprawidłowe transakcje.')
    ids = set()
    for row in rows:
        if not all(field in row for field in BASE_FIELDS) or row['id'] in ids:
            raise ValueError('Nieprawidłowy identyfikator transakcji.')
        ids.add(row['id'])
        if row['kind'] not in ['buy', 'dividend', 'interest', 'expected_dividend'] or row['asset'] not in ['Akcje', 'ETF', 'Obligacje']:
            raise ValueError('Nieprawidłowy rodzaj transakcji.')
        if not row['name'] or not row['symbol']:
            raise ValueError('Nazwa i symbol są wymagane.')
        for field in ['quantity', 'price', 'current']:
            value = row[field]
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError('Nieprawidłowa kwota lub liczba sztuk.')
        if row['quantity'] <= 0:
            raise ValueError('Liczba sztuk musi być dodatnia.')
        day(row['date'])
        if row.get('bond_terms'):
            terms = json.loads(row['bond_terms'])
            rate = float(terms['rate'])
            if not math.isfinite(rate) or not 0 <= rate <= 100:
                raise ValueError('Nieprawidłowe oprocentowanie obligacji.')

def fetch_dividends(symbol, token, since):
    query = urllib.parse.urlencode({'api_token': token, 'fmt': 'json', 'from': since})
    url = 'https://eodhd.com/api/div/' + urllib.parse.quote(symbol, safe='.') + '?' + query
    with urllib.request.urlopen(url, timeout=15) as response:
        result = json.load(response)
    if not isinstance(result, list):
        raise ValueError('Dostawca zwrócił nieprawidłową odpowiedź.')
    return result


def parse_bond_offer(html, catalog):
    class Text(HTMLParser):
        def __init__(self):
            super().__init__()
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data.strip())
    parser = Text()
    parser.feed(html)
    text = ' '.join(parser.parts)
    blocks = re.split(r'Seria:\s*', text)
    known = {item['symbol']:item for item in catalog}
    profiles = {item['symbol'][:3]:item for item in catalog}
    found = {}
    for block in blocks[1:]:
        symbol = re.match(r'((?:OTS|ROR|DOR|TOS|COI|EDO|ROS|ROD)\d{4})\b', block)
        rate = re.search(r'Oprocentowanie\s+(\d+(?:[,.]\d+)?)\s*%', block)
        price = re.search(r'Cena zakupu\s+(\d+(?:[,.]\d+)?)', block)
        if not symbol or not rate or not price:
            continue
        code = symbol[1]
        profile = dict(known.get(code) or profiles[code[:3]])
        if code not in known:
            profile['rule'] = 'Stawka oferty. Dla serii zmiennych dotyczy pierwszego okresu; kolejne warunki sprawdź w liście emisyjnym.'
        years = {'ROR':1,'DOR':2,'TOS':3,'COI':4,'EDO':10,'ROS':6,'ROD':12}
        year, month = 2000+int(code[-2:]), int(code[3:5])
        if code[:3] == 'OTS':
            month -= 3
            if month <= 0:
                month += 12
                year -= 1
        else:
            year -= years[code[:3]]
        profile.update(symbol=code, rate=float(rate[1].replace(',','.')), price=float(price[1].replace(',','.')),
                       verified=date.today().isoformat(), mode='live', sale_from=f'{year:04d}-{month:02d}-01',
                       sale_to=f'{year:04d}-{month:02d}-{calendar.monthrange(year,month)[1]}')
        found[code] = profile
    if not found:
        raise ValueError('Nie rozpoznano oferty obligacji.')
    return list(found.values())


def bond_catalog():
    catalog = json.loads((ROOT / 'obligacje.json').read_text(encoding='utf-8'))
    cache = DATA.parent / 'oferta-obligacji.json'
    if cache.exists():
        stored = json.loads(cache.read_text(encoding='utf-8'))
        catalog = stored['items']
        if stored['checked'] == date.today().isoformat():
            return catalog, ''
    try:
        with urllib.request.urlopen('https://www.obligacjeskarbowe.pl/oferta/', timeout=15) as response:
            html = response.read().decode(response.headers.get_content_charset() or 'utf-8')
        latest = parse_bond_offer(html, catalog)
        combined = {item['symbol']:item for item in catalog}
        combined.update({item['symbol']:item for item in latest})
        catalog = list(combined.values())
        with LOCK:
            atomic_text(cache, json.dumps({'checked':date.today().isoformat(), 'items':catalog}, ensure_ascii=False))
        return catalog, ''
    except Exception:
        return catalog, 'Nie udało się odświeżyć oferty obligacji. Pokazujemy zapisaną ofertę z datą weryfikacji; sprawdź serię i warunki.'


def search_instruments(query, asset):
    catalog, warning = bond_catalog() if asset in ['', 'Obligacje'] else ([], '')
    results = [item for item in catalog if asset in ['', 'Obligacje'] and
               all(term in (item['symbol']+' '+item['name']).casefold() for term in query.casefold().split())]
    if asset != 'Obligacje':
        token = read_config().get('token')
        if not token:
            warning = 'Wyszukiwanie akcji i ETF-ów wymaga klucza EODHD w ustawieniach dywidend. Możesz też wpisać instrument ręcznie.'
        else:
            kind = {'Akcje':'stock', 'ETF':'etf'}.get(asset, 'all')
            params = urllib.parse.urlencode({'api_token':token, 'fmt':'json', 'limit':12, 'type':kind})
            url = 'https://eodhd.com/api/search/'+urllib.parse.quote(query, safe='')+'?'+params
            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    found = json.load(response)
                if not isinstance(found, list):
                    raise ValueError()
                for item in found:
                    if item.get('Type') not in ['Common Stock', 'ETF']:
                        continue
                    results.append({'symbol':item['Code']+'.'+item['Exchange'], 'name':item['Name'],
                                    'asset':'ETF' if item['Type']=='ETF' else 'Akcje', 'currency':item.get('Currency', ''),
                                    'exchange':item['Exchange']})
            except Exception:
                warning = 'Nie udało się wyszukać akcji i ETF-ów. Sprawdź klucz EODHD, dostęp do danych i połączenie.'
    return {'items':results, 'warning':warning}

def merge_events(rows, symbol, provider_symbol, events):
    """Only purchases strictly before ex-date qualify. No sale/split ledger yet."""
    buys = [r for r in rows if r['kind'] == 'buy' and r['symbol'] == symbol and r['asset'] in ['Akcje', 'ETF']]
    by_event = {r['event_id']: r for r in rows if r.get('event_id')}
    added = updated = 0
    for event in events:
        ex_date = day(event['date'])
        eligible = [r for r in buys if r['date'] < ex_date]
        quantity = sum(r['quantity'] for r in eligible)
        if quantity <= 0:
            continue
        # A quote currency must never be silently treated as PLN.
        currency = event.get('currency')
        if not currency or not re.fullmatch(r'[A-Z]{3}', currency):
            raise ValueError('Brak waluty dywidendy w danych dostawcy.')
        amount = float(event.get('unadjustedValue') if event.get('unadjustedValue') is not None else event['value'])
        if not math.isfinite(amount) or amount < 0:
            raise ValueError('Nieprawidłowa kwota dywidendy.')
        payment = event.get('paymentDate') or ''
        if payment:
            payment = day(payment)
        # Stable across payment-date or amount corrections.
        event_id = f'eodhd:{provider_symbol}:{ex_date}'
        previous = by_event.get(event_id)
        if previous and previous['kind'] != 'expected_dividend':
            continue
        row = dict(id=previous['id'] if previous else str(uuid.uuid4()), name=eligible[0]['name'], symbol=symbol,
                   asset=eligible[0]['asset'], kind='expected_dividend', date=payment or ex_date,
                   quantity=quantity, price=0, current=0, event_id=event_id, status='expected', currency=currency,
                   ex_date=ex_date, payment_date=payment, per_share=str(amount), expected_amount=str(round(quantity * amount, 8)),
                   source=f'https://eodhd.com/financial-apis/api-splits-dividends', synced_at=datetime.now(timezone.utc).isoformat())
        if previous:
            previous.update(row)
            updated += 1
        else:
            rows.append(row)
            by_event[event_id] = row
            added += 1
    return added, updated

def sync_dividends(force=False):
    with SYNC_LOCK:
        with LOCK:
            config = read_config()
            rows = read_rows()
        if not config.get('token'):
            raise ValueError('Najpierw wpisz klucz API EODHD w ustawieniach dywidend.')
        symbols = sorted({r['symbol'] for r in rows if r['kind'] == 'buy' and r['asset'] in ['Akcje', 'ETF']})
        today = date.today().isoformat()
        checked = config.get('checked', {})
        errors = []
        added = updated = 0
        for symbol in symbols:
            provider_symbol = config.get('symbols', {}).get(symbol) or (symbol if re.fullmatch(r'[A-Za-z0-9_^=+.-]+\.[A-Za-z0-9]+', symbol) else None)
            if not provider_symbol:
                errors.append(f'{symbol}: wskaż symbol z giełdą w ustawieniach.')
                continue
            if not force and checked.get(symbol) == today:
                continue
            since = min(r['date'] for r in rows if r['symbol'] == symbol and r['kind'] == 'buy')
            try:
                events = fetch_dividends(provider_symbol, config['token'], since)
                with LOCK:
                    fresh = read_rows()
                    a, u = merge_events(fresh, symbol, provider_symbol, events)
                    write_rows(fresh)
                    added += a
                    updated += u
                checked[symbol] = today
            except Exception:
                # Never expose upstream URLs that contain the API token.
                errors.append(f'{symbol}: nie udało się pobrać pełnych danych. Sprawdź symbol, klucz API i dostęp w abonamencie.')
        with LOCK:
            config['checked'] = checked
            config['errors'] = errors
            write_config(config)
        return {'added': added, 'updated': updated, 'errors': errors}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        pass

    def allowed(self):
        return self.headers.get('Host') in [f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}']

    def output(self, data, status=200):
        payload = json.dumps(data, allow_nan=False, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def body(self):
        if not self.allowed() or self.headers.get('Origin') != f'http://{self.headers.get("Host")}':
            raise PermissionError('Niedozwolone źródło żądania.')
        length = int(self.headers.get('Content-Length', 0))
        if not 0 < length <= 5_000_000:
            raise ValueError('Nieprawidłowa wielkość danych.')
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        if not self.allowed():
            return self.send_error(403)
        try:
            with LOCK:
                if self.path == '/api/portfolio':
                    return self.output({'rows': read_rows(), 'revision': revision()})
                if self.path == '/api/history':
                    return self.output({'prices': portfolio_history(read_rows())})
                if self.path == '/api/dividends/settings':
                    return self.output(public_config(read_config()))
            # Never serve CSV or API secrets as static files or directory listings.
            if self.path.split('?')[0] not in ['/', '/index.html', '/style.css', '/app.js', '/dividends.js', '/history.js', '/instruments.js', '/obligacje.json']:
                return self.send_error(404)
            return super().do_GET()
        except Exception:
            self.output({'error': 'Nie udało się odczytać danych. Sprawdź plik CSV; nie został nadpisany.'}, 500)

    def do_PUT(self):
        try:
            data = self.body()
            with LOCK:
                if self.path == '/api/portfolio':
                    current = read_rows()
                    if data.get('revision') != revision():
                        raise Conflict('Dane zmieniły się w innym oknie. Odśwież stronę przed ponowną edycją.')
                    validate_rows(data['rows'])
                    write_rows(data['rows'])
                    return self.output({'revision': revision()})
                if self.path == '/api/dividends/settings':
                    config = read_config()
                    mappings = data.get('symbols', {})
                    if not isinstance(mappings, dict) or any(not re.fullmatch(r'[A-Za-z0-9_^=+.-]+\.[A-Za-z0-9]+', v) for v in mappings.values()):
                        raise ValueError('Podaj symbol w formacie dostawcy, np. AAPL.US lub KTY.WAR.')
                    if len(set(mappings.values())) != len(mappings):
                        raise ValueError('Jeden symbol EODHD przypisz do jednego symbolu w portfelu. Połącz zakupy tej samej spółki pod wspólnym symbolem.')
                    token = data.get('token', '').strip()
                    if token:
                        config['token'] = token
                    if mappings != config.get('symbols') or token:
                        config['checked'] = {}
                    config['symbols'] = mappings
                    write_config(config)
                    return self.output(public_config(config))
            self.send_error(404)
        except PermissionError as error:
            self.output({'error': str(error)}, 403)
        except Conflict as error:
            self.output({'error': str(error)}, 409)
        except Exception as error:
            self.output({'error': str(error) if isinstance(error, ValueError) else 'Nie udało się zapisać danych.'}, 400)

    def do_POST(self):
        try:
            data = self.body()
            if self.path == '/api/instruments/search':
                query = str(data.get('query', '')).strip()
                asset = data.get('asset', '')
                if not 2 <= len(query) <= 100 or asset not in ['', 'Akcje', 'ETF', 'Obligacje']:
                    raise ValueError('Wpisz od 2 do 100 znaków i poprawny rodzaj instrumentu.')
                return self.output(search_instruments(query, asset))
            if self.path == '/api/dividends/sync':
                return self.output(sync_dividends(bool(data.get('force'))))
            if self.path == '/api/dividends/confirm':
                amount = float(data['amount'])
                actual_date = day(data['date'])
                if not math.isfinite(amount) or amount < 0 or actual_date > date.today().isoformat():
                    raise ValueError('Podaj otrzymaną kwotę i datę nie późniejszą niż dzisiaj.')
                with LOCK:
                    rows = read_rows()
                    row = next((r for r in rows if r['id'] == data['id']), None)
                    if not row or row['kind'] != 'expected_dividend':
                        raise ValueError('Ten wpływ został już potwierdzony lub usunięty. Odśwież stronę.')
                    row.update(kind='dividend', status='confirmed', price=amount, date=actual_date)
                    write_rows(rows)
                return self.output({'ok': True})
            self.send_error(404)
        except PermissionError as error:
            self.output({'error': str(error)}, 403)
        except Exception as error:
            self.output({'error': str(error) if isinstance(error, ValueError) else 'Operacja nie powiodła się. Spróbuj ponownie.'}, 400)

def main():
    global DATA
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8766)
    parser.add_argument('--data-dir', type=Path, default=DATA.parent)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()
    DATA = args.data_dir.resolve() / 'portfel.csv'
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Saldo: http://127.0.0.1:{server.server_port} — close this window to stop.', flush=True)
    if not args.no_browser:
        threading.Timer(0.7, lambda: webbrowser.open(f'http://127.0.0.1:{server.server_port}')).start()
    server.serve_forever()

if __name__ == '__main__':
    main()
