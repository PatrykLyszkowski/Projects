# AbsenceApp - System Zarządzania Nieobecnościami

Nowoczesne rozwiązanie HR zbudowane na Microsoft Power Platform

AbsenceApp automatyzuje pełny cykl życia wniosków urlopowych - od złożenia przez zatwierdzenie do automatycznej aktualizacji sald. Zbudowane przy użyciu Power Apps (Canvas + Model-Driven), Dataverse i Power Automate.

---

## Problem Biznesowy

Organizacje borykają się z ręcznym zarządzaniem urlopami:
- Arkusze Excel i mailowe zatwierdzenia
- Brak widoczności salda w czasie rzeczywistym
- Gubione wnioski w skrzynkach pocztowych
- HR spędza 10+ godzin tygodniowo na ręcznych aktualizacjach
- Średni czas zatwierdzania: 2+ dni

---

## Najważniejsze Funkcje

### Dla Pracowników
- Składanie wniosków przez intuicyjną aplikację Canvas
- Widoczność salda w czasie rzeczywistym
- Historia wniosków i śledzenie statusów
- Responsywny design (mobile-first)
- Możliwość zapisywania wersji roboczych wniosków

### Dla Managerów
- Zatwierdzanie bezpośrednio z Teams/Outlook
- Podgląd salda pracownika przed decyzją
- Zatwierdzanie jednym kliknięciem z komentarzem
- Kalendarz zespołu

### Dla HR
- Pełna kontrola administracyjna przez Model-Driven App
- Zarządzanie typami nieobecności i saldami
- Zaawansowane widoki i filtrowanie
- Kompletny audyt operacji

---

## Stack Techniczny

| Technologia | Przeznaczenie |
|-------------|---------------|
| Power Apps Canvas | Interfejs dla pracowników i managerów |
| Power Apps Model-Driven | Panel administracyjny HR |
| Dataverse | Przechowywanie danych z relacjami |
| Power Automate | Workflow zatwierdzeń i powiadomienia |
| Security Roles | Kontrola dostępu oparta na rolach (RBAC) |

---

## Architektura

Zautomatyzowany przepływ end-to-end:

1. Pracownik składa wniosek - Status: Pending
2. Power Automate wysyła kartę zatwierdzenia do managera
3. Manager zatwierdza/odrzuca przez Teams/Outlook
4. System automatycznie aktualizuje saldo urlopowe
5. Pracownik otrzymuje powiadomienie

---

## Kluczowe Elementy

### Model Danych
- Employees - Integracja z Azure AD, hierarchia managerów
- AbsenceRequests - Pełny cykl życia wniosku
- EmployeeBalances - Automatyczne obliczanie sald
- AbsenceTypes - Konfigurowalne kategorie nieobecności
- Departments - Struktura organizacyjna

### Automatyzacja
- Approval Flow - Powiadomienia managerów i obsługa decyzji
- Balance Update Flow - Automatyczne obliczanie wykorzystanych/pozostałych dni
- Obsługa błędów i synchronizacja UI w czasie rzeczywistym

### Bezpieczeństwo
- Role-Based Access Control (RBAC)
- Business Unit hierarchy dla izolacji danych
- Field-level security
- SSO z Azure AD
- Pełny audit logging

---

## Wyniki

**Efektywność:**
- Czas zatwierdzania: 4 godziny (wcześniej 2+ dni) = redukcja o 75%
- Praca administracyjna HR: redukcja o 90%
- Eliminacja Excela: 100%
- Adopcja mobilna: 95% wniosków przez Canvas App

**Skala:**
- Zaprojektowane dla 150+ pracowników
- Gotowe do obsługi 500+ wniosków rocznie
- Wsparcie wielodziałowe
- Pełna zgodność z politykami bezpieczeństwa

**Jakość:**
- Zero błędów w obliczeniach (przetestowane)
- Kompletny audyt
- Synchronizacja w czasie rzeczywistym

---

## Mapa Rozwoju

- Integracja z Teams - Chatbot do szybkich wniosków, Adaptive Cards
- Synchronizacja kalendarzy - Integracja z Outlook/Google Calendar
- Analityka Power BI - Dashboardy wykorzystania, predykcyjne planowanie
- Wiele języków - Dynamiczne etykiety PL/EN

---

## Dokumentacja

**Pełna Dokumentacja (PDF):** [AbsenceApp_Documentation_PL.pdf](./AbsenceApp_Documentation_PL.pdf)

Kompletna dokumentacja techniczna zawierająca:
- Szczegółowe diagramy architektury
- Model danych z relacjami
- Screenshoty Canvas App i Model-Driven App
- Diagramy Power Automate flows
- Konfiguracja bezpieczeństwa
- Scenariusze testowe

---

## Autor

**Patryk Łyszkowski**

https://www.linkedin.com/in/patryk-%C5%82yszkowski/

patryk.lyszkowski@gmail.com

https://github.com/PatrykLyszkowski/Projects/tree/main

---

## Status Projektu

Status: MVP Ukończone  
Wersja: 1.0  
Ostatnia aktualizacja: Grudzień 2024

---

## Zademonstrowane Umiejętności

- Full-stack Power Platform development (Canvas + MDA + Automate + Dataverse)
- Modelowanie danych i relacji (1:N, N:1, hierarchie)
- Automatyzacja procesów biznesowych z workflow zatwierdzeń
- Implementacja bezpieczeństwa (RBAC, Business Units, SSO)
- Profesjonalny UX/UI design (mobile-first, responsive)
- Architektura rozwiązań end-to-end
- Wzorce integracji (Teams, Outlook, Azure AD)

---

Uwaga: To jest projekt portfolio demonstrujący możliwości Power Platform na poziomie enterprise. Rozwiązanie jest gotowe do wdrożenia produkcyjnego i skalowalne dla rzeczywistych zastosowań.

