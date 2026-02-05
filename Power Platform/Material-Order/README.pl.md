# Material Order System

> **Systemowe Rozwiązanie do Zarządzania Zamówieniami Materiałów** zbudowane na Microsoft Power Platform  
> *Automatyzacja procesów zakupowych od zgłoszenia do realizacji*

[English version](README.md) | [Pełna Dokumentacja Techniczna (PDF - wersja PL)](https://github.com/PatrykLyszkowski/Projects/raw/main/Power%20Platform/Material-Order/docs/Material_Order_Dokumentacja_PL.pdf)

---

## Przegląd

**Material Order** to kompleksowy system zarządzania zamówieniami materiałów, który usprawnia cały proces zakupowy dla firm budowlanych i produkcyjnych. Rozwiązanie automatyzuje procesy zatwierdzania, integruje się z Microsoft Teams i zapewnia kontrolę dostępu opartą na rolach dla brygadzistów, kierowników i dostawców.

### Kluczowe Możliwości

- **Zarządzanie Wielopozycyjnymi Zamówieniami** – Tworzenie złożonych zamówień z wieloma pozycjami, ilościami i jednostkami
- **Warunkowe Procesy Zatwierdzania** – Konfigurowalne wymagania akceptacji dla każdego projektu
- **Powiadomienia w Teams w Czasie Rzeczywistym** – Interaktywne Adaptive Cards do natychmiastowych zatwierdzeń
- **Kontrola Dostępu Oparta na Rolach** – Oddzielne interfejsy dla Pracowników, Kierowników i Dostawców
- **Pełne Śledzenie Cyklu Życia** – Od wersji roboczej przez realizację do zakończenia
- **Projekt Mobile-first** – Zoptymalizowany dla tabletów i urządzeń mobilnych w terenie

---

## Architektura

### Stack Techniczny

| Warstwa | Technologia |
|---------|-----------|
| **Prezentacja** | Canvas App (osadzony w Teams) |
| **Logika Biznesowa** | Power Automate (Cloud Flows) |
| **Warstwa Danych** | Microsoft Dataverse |
| **Integracja** | Teams Connector, Dataverse Connector |
| **Autentykacja** | Azure AD (przez Teams) |

### Model Danych

System wykorzystuje cztery niestandardowe tabele Dataverse z rozbudowanymi relacjami:

- **CompanyUser** – Zarządzanie użytkownikami z przypisaniem ról
- **Project** – Projekty budowlane z ustawieniami akceptacji
- **Order** – Główna tabela zamówień z 7-etapowym cyklem życia
- **OrderItem** – Pozycje zamówienia ze śledzeniem ilości (relacja 1:N)

**Cykl Życia Zamówienia:**  
`Wersja robocza` → `Wysłane` → `Zatwierdzone` → `W realizacji` → `Zakończone`  
*(Alternatywne ścieżki: `Odrzucone`, `Wymagane zmiany`)*

---

## Główne Funkcjonalności

### 1. Inteligentne Tworzenie Zamówień
- Dynamiczny kreator listy materiałów
- Automatyczne dziedziczenie adresu dostawy z projektów
- Routing oparty na priorytetach (Niski/Normalny/Wysoki/Pilny)
- Przypisywanie dostawców z wyszukiwaniem email

### 2. Zautomatyzowany Proces Akceptacji
- **Warunkowy routing** oparty na konfiguracji projektu
- **Adaptive Cards** w Teams z 3 akcjami:
  - Zatwierdź
  - Odrzuć  
  - Poproś o zmiany
- Automatyczna aktualizacja statusów i znaczników czasu
- Powiadomienie kierownika przy ponownym wysłaniu

### 3. Interfejs Realizacji dla Dostawców
- Dedykowany ekran dla przypisanych zamówień
- Śledzenie zakupów pozycja po pozycji
- Monitoring postępu z wskaźnikami procentowymi
- Notatki dotyczące dostawy i workflow zakończenia

### 4. Zaawansowane PowerFX

Aplikacja demonstruje rozwój Power Apps na poziomie enterprise:

```powerfx
// Statystyki oparte na rolach ze złożonym filtrowaniem
Set(varNeedsAttention,
    Filter(
        Orders,
        RequestedBy.Email = varCurrentUser.Email &&
        (
            'Status (status)' = 'Status (Orders)'.'Changes Requested' ||
            'Status (status)' = 'Status (Orders)'.Rejected ||
            (
                'Status (status)' = 'Status (Orders)'.'Partially Completed' &&
                StartedOn < varTwoDaysAgo
            )
        )
    )
);
```

**Zastosowane Kluczowe Techniki:**
- Dwuetapowe filtrowanie dla optymalizacji wydajności
- Operacje masowe ForAll dla pozycji zamówienia
- Konwersja enum oparta na Switch dla bezpieczeństwa typów
- Tymczasowe przechowywanie oparte na kolekcjach
- Zaawansowane wzorce delegacji

---

## Wartość Biznesowa

### Rozwiązane Problemy
- Manualne procesy zatwierdzania przez email/chat
- Zagubione lub zapomniane zlecenia materiałowe
- Brak widoczności statusu zamówień
- Wyzwania koordynacji z dostawcami
- Niekompletny ślad audytowy

### Korzyści z Rozwiązania
- **O 60% szybsze czasy zatwierdzania** dzięki natychmiastowym powiadomieniom Teams
- **Zero zagubionych zleceń** dzięki scentralizowanemu śledzeniu
- **Widoczność w czasie rzeczywistym** dla wszystkich interesariuszy
- **Automatyczny ślad audytowy** ze śledzeniem historii Dataverse
- **Dostępność mobilna** dla pracowników w terenie

---

## Wdrożenie

### Wymagania Wstępne
- Microsoft 365 E3/E5 lub Business Premium
- Licencja Power Apps per-user lub per-app
- Power Automate Premium (konektor Dataverse)
- Pojemność bazy danych Dataverse
- Dostęp administratora Teams do wdrożenia aplikacji

### Kroki Instalacji
1. Utworzenie środowiska produkcyjnego z Dataverse
2. Import pakietu rozwiązania
3. Konfiguracja referencji połączeń (Dataverse, Teams)
4. Aktualizacja ID kanałów Teams w przepływach
5. Włączenie przepływów automatyzacji
6. Przesłanie aplikacji niestandardowej do Teams App Studio
7. Wypełnienie tabeli CompanyUser danymi organizacyjnymi

*Zobacz pełną dokumentację dla szczegółowych instrukcji konfiguracji*

---

## Bezpieczeństwo

### Kontrola Dostępu do Danych
- **Pracownicy** – Przeglądają tylko własne zamówienia
- **Dostawcy** – Dostęp do przypisanych zamówień z prawami edycji
- **Kierownicy** – Pełna widoczność wszystkich projektów

Implementacja:
- Filtrowanie oparte na rolach w Canvas App
- Bezpieczeństwo na poziomie wierszy Dataverse
- Udostępnianie rekordów oparte na właścicielu
- Autentykacja Azure AD przez Teams

---

## Dokumentacja

Dostępna kompleksowa dokumentacja techniczna obejmująca:
- Kompletny model danych z diagramami ERD
- Konfiguracja przepływów Power Automate
- Przykłady zaawansowanego kodu PowerFX
- Przewodnik instalacji i konfiguracji
- Scenariusze użycia i workflow

[Pobierz Pełną Dokumentację (PDF)](docs/Material_Order_Dokumentacja_PL.pdf)

---

## Zademonstrowane Umiejętności

Ten projekt prezentuje profesjonalne możliwości rozwoju Power Platform:

### Power Apps Canvas
- Złożona nawigacja wieloekranowa
- Zarządzanie zmiennymi globalnymi (30+ zmiennych)
- System motywów (tryb jasny/ciemny)
- Responsywny design dla Teams
- Techniki optymalizacji wydajności

### Power Automate
- Wyzwalacze i akcje Dataverse
- Konstrukcja JSON Adaptive Card
- Warunkowa logika workflow
- Wzorce obsługi błędów
- Integracja z Teams

### Dataverse
- Modelowanie danych relacyjnych
- Kolumny wyboru i enumy
- Relacje Lookup (1:N)
- Reguły kaskadowego usuwania
- Konfiguracja autonumeracji

### PowerFX
- Zaawansowane filtrowanie z delegacją
- Manipulacja kolekcjami
- Operacje masowe ForAll
- Logika warunkowa Switch/If
- Konwersja enum bezpieczna typowo

---

## Kontakt

**Patryk Lyszkowski**  
Power Platform Developer

- LinkedIn: [linkedin.com/in/patryk-lyszkowski](https://linkedin.com/in/patryk-lyszkowski)
- GitHub: [github.com/PatrykLyszkowski](https://github.com/PatrykLyszkowski)
- Dostępny na konsultacje i rozwój niestandardowy

---

## Wersja

**Aktualna Wersja:** 1.0.0.9  
**Ostatnia Aktualizacja:** Luty 2025  
**Status:** Gotowe do produkcji

---


*Zbudowane na Microsoft Power Platform • Zaprojektowane dla Skali Enterprise*




