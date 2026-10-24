SALDO — prywatny portfel

Uruchom Uruchom.cmd i korzystaj z adresu http://127.0.0.1:8766.
Nie otwieraj samego index.html, jeśli chcesz zapisywać dane do CSV.
Wymagany Python 3.10 lub nowszy. Nie trzeba instalować bibliotek.

DANE
Źródłem danych jest dane/portfel.csv. Plik powstaje automatycznie.
Po ponownym uruchomieniu serwer odczytuje go niezależnie od pamięci przeglądarki.
Zapis używa pliku tymczasowego i atomowej podmiany. Błąd odczytu nie zeruje CSV.
Starszy format CSV jest obsługiwany i rozszerzany przy kolejnym zapisie.
Nie edytuj jednocześnie CSV i otwartej aplikacji. Eksport pobiera kopię danych.

DYWIDENDY
W widoku Dywidendy i odsetki wybierz Ustawienia.
Wpisz własny klucz API EODHD. Aplikacja nie kupuje abonamentu.
Do zakupów akcji i ETF-ów przypisz zweryfikowany symbol EODHD z giełdą,
np. AAPL.US lub KTY.WAR. Pokrycie danych zależy od dostawcy i abonamentu.
Klucz pozostaje w dane/ustawienia.json i jest wysyłany wyłącznie do EODHD.
Pliku ustawień nie udostępniaj innym osobom. Nie jest dostępny przez serwer WWW.

Po konfiguracji aplikacja sprawdza dane przy otwarciu, a potem co godzinę,
gdy karta jest widoczna. Udane pobranie dla instrumentu odbywa się najwyżej
raz na dzień. Przycisk Pobierz dywidendy wymusza odświeżenie.
Aplikacja zamknięta nie pobiera danych w tle; nadrobi je po uruchomieniu.
Nie zakłada istnienia przyszłej dywidendy na podstawie wypłat historycznych.
Pobiera ogłoszenia dostępne u dostawcy od pierwszego zakupu danego instrumentu.

Oczekiwane wpływy mają osobny rodzaj expected_dividend w tym samym CSV.
Ich kwota brutto pozostaje w walucie źródłowej i nie zwiększa wyniku portfela.
Zakupy z dnia ex-date i późniejsze nie są zaliczane do uprawnionych sztuk.
Wersja pierwsza nie obsługuje sprzedaży, splitów ani transferów — uprawnienie
wynika tylko z historii zakupów i wymaga weryfikacji z rachunkiem brokera.
Przy braku daty wypłaty aplikacja pokazuje Termin nieznany.

Po wypłacie użyj Potwierdź wpływ: podaj otrzymaną kwotę netto w PLN i datę.
Ten sam wpis zmienia status na potwierdzony i trafia do otrzymanych dywidend.
Waluta oryginalnej oczekiwanej kwoty pozostaje w metadanych CSV; price po
potwierdzeniu oznacza rzeczywistą kwotę w PLN. Brak automatycznego FX i podatku.
Ponowne pobranie nie nadpisuje potwierdzonej kwoty ani nie dubluje wpływu.

TESTY
python test_portfel.py
Testy używają osobnych katalogów i rzeczywistych restartów lokalnego serwera.
Dane EODHD w testach są kontrolowane; nie potrzeba klucza ani płatnych wywołań.

HISTORIA PORTFELA
Pulpit pokazuje koszt zakupów, wartość instrumentów + otrzymane wypłaty oraz
różnicę między nimi (wynik w PLN). Brak osobnej ewidencji wpłat gotówki.
Dzienne ręczne wyceny są zapisywane w dane/historia.csv przy odczycie portfela
i po zmianach. Ten sam dzień jest aktualizowany, wcześniejsze dni pozostają.
Kopiuj oba pliki CSV, aby zachować portfel wraz z historią wycen.
Wcześniejsze nieznane wyceny nie są rekonstruowane z dzisiejszych cen.
Prognoza pozostaje wyłącznie w widoku Plan na przyszłość.
Test obliczeń wykresu: node test_history.js

WYSZUKIWANIE INSTRUMENTÓW
W formularzu zakupu wpisz nazwę, serię lub ISIN i kliknij Szukaj.
Akcje i ETF-y: wyszukiwanie przez EODHD, wymaga własnego klucza.
Wybór notowania nie oznacza automatycznego przeliczenia ceny z obcej waluty;
cenę faktycznego zakupu podaj w PLN. Wybrana giełda pozostaje w symbolu.
Obligacje: oficjalna oferta obligacjeskarbowe.pl odświeżana najwyżej raz dziennie.
Przy błędzie używamy zapisanej oferty z datą weryfikacji, bez ukrywania błędu.
Przechowujemy poznane serie; katalog początkowy obejmuje ofertę 10/2026.
Starszą nieznaną serię można dodać ręcznie z oprocentowaniem z dokumentów.
Wybrana seria uzupełnia pierwszą stopę i cenę 100 PLN. Cenę możesz zmienić.
Pole obecnej ceny usunięto z formularza. Wycena startuje od kosztu zakupu.
Oprocentowanie i warunki są zapisane w kolumnie bond_terms w CSV.
Nie wyliczamy jeszcze automatycznie odsetek ani kolejnych stóp inflacja/NBP.
Dla obligacji zmiennych podana stopa nie obowiązuje przez cały czas inwestycji.
