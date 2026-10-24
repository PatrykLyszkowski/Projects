# Saldo

Prywatna aplikacja do monitorowania akcji, ETF-ów i obligacji skarbowych. Działa lokalnie, a transakcje i historia wycen są zapisywane w CSV na komputerze użytkownika.

## Uruchomienie

Wymagania: Python 3.10+ i współczesna przeglądarka. Biblioteki Pythona nie wymagają instalowania.

Po pobraniu repozytorium otwórz folder `Saldo` i uruchom `Uruchom.cmd` albo wpisz:

```powershell
python server.py
```

Otwórz <http://127.0.0.1:8766>. Pozostaw serwer uruchomiony podczas korzystania z aplikacji. Samo otwarcie `index.html` nie uruchamia zapisu do CSV ani integracji internetowych.

## Funkcje

- Ręczne dodawanie zakupów: instrument, data, liczba sztuk i cena zakupu w PLN.
- Portfel akcji, ETF-ów i obligacji oraz ręczna aktualizacja wycen.
- Historia zainwestowanego kapitału, wartości z otrzymanymi wypłatami i wyniku w PLN.
- Dywidendy i odsetki; pobieranie oczekiwanych dywidend z EODHD i potwierdzanie rzeczywistego wpływu.
- Wyszukiwanie akcji i ETF-ów przez EODHD po skonfigurowaniu własnego klucza.
- Wyszukiwanie aktualnych serii detalicznych obligacji skarbowych z uzupełnianiem pierwszej stopy oprocentowania.
- Osobny symulator regularnych wpłat i założonej średniorocznej stopy zwrotu.
- Eksport CSV i zachowanie danych po restarcie serwera.

## Dane i integracje

Folder `dane/` powstaje automatycznie. Zawiera portfel, dzienne obserwacje wycen, pamięć oferty obligacji i ustawienia integracji. Jest pomijany przez Git i nie należy go publikować. Klucz EODHD zapisuje się lokalnie w `dane/ustawienia.json`; aplikacja nie udostępnia tego pliku przez serwer WWW. Własny klucz i odpowiedni zakres dostępu EODHD są wymagane dla integracji z tym dostawcą.

Pobieranie danych odbywa się podczas działania aplikacji. Zamknięta aplikacja nie pracuje w tle. Oferta obligacji pochodzi z <https://www.obligacjeskarbowe.pl/oferta/>. W razie błędu dostępny jest zapisany katalog z datą weryfikacji.

## Zakres pierwszej wersji

Wszystkie rozliczenia portfela są w PLN. Nie ma automatycznego przeliczania walut, naliczania podatku, obsługi sprzedaży, splitów ani transferów. Linia kapitału oznacza koszty zakupów, a nie oddzielną ewidencję wpłat gotówki. Nieznane historyczne wyceny nie są odtwarzane z dzisiejszych cen. Oprocentowanie obligacji dotyczy pierwszego okresu; kolejne stopy i odsetki nie są jeszcze naliczane automatycznie.

## Testy

```powershell
python test_portfel.py
node test_history.js
```

Python testuje lokalny serwer, CSV, restart, dywidendy i warunki obligacji na oddzielnych plikach oraz kontrolowanych danych dostawcy. Test obliczeń wykresu wymaga Node.js. Testy nie wymagają klucza API ani płatnych wywołań.

Szczegóły działania: [README.txt](README.txt).
