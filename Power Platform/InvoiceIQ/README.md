ENG
# InvoiceIQ

**InvoiceIQ** is a Power Apps application that streamlines the entire invoice management process.  
Instead of scattered emails and files, all invoices are stored in one place – easy to track, assign, update status, and control payments.

---

## Features

- **Check Invoices** – main list view, key invoice details, status updates, ownership, counters.
- **Kanban Board** – visual workflow, drag & drop invoices between statuses (New, Parsed, NeedReview, Approved, Rejected).
- **Payments** – schedule, hold, and process payments; mark invoices as *Processing* or *Paid*.
- **Reports (planned)** – Power BI dashboards (KPIs, totals, rejection stats).
- **Admin Panel (planned)** – user roles, data sources, and integrations.

---

## Roles & Permissions

- **Administrator** – full access to all modules.  
- **Reviewers** – access to *Check Invoices* and *Kanban* for verification.  
- **Payments team** – access only to the *Payments* module.  

This ensures security and clarity – each user only sees what is needed.

---

## Automations

InvoiceIQ integrates with **Power Automate** and **AI Builder**:  
- Power Automate detects new PDFs in SharePoint and triggers workflows.  
- AI Builder OCR extracts invoice data (number, vendor, dates, amounts).  
- Extracted data is saved to a **SharePoint list**, used by the app.  

---

## Documentation

- [Full documentation (PDF)](./docs/InvoiceIQ_Documentation.pdf)  
- [Process diagram (PNG)](./assets/diagram.png)  

---

## Roadmap

- Scan invoices with a phone (OCR).  
- Alerts for new invoices and payment deadlines.  
- Power BI dashboards.  
- Integrations with ERP, accounting, and banking systems.  

---

## Status

- **v1.0** – First release: Check Invoices, Kanban, Payments, OCR automation.  
- Next: Reports + Admin Panel.  

PL

# InvoiceIQ

**InvoiceIQ** to aplikacja zbudowana w Power Apps, która upraszcza proces obsługi faktur.  
Zamiast gubić się w mailach i plikach, wszystkie faktury są w jednym miejscu – można je łatwo sprawdzić, przypisać, zmienić status i kontrolować płatności.

---

## Funkcje

- **Check Invoices** – główny widok listy, szczegóły faktur, zmiana statusów, właściciel, liczniki.  
- **Kanban Board** – tablica z fakturami w kolumnach wg statusów (New, Parsed, NeedReview, Approved, Rejected).  
- **Payments** – planowanie, wstrzymywanie i realizacja płatności; oznaczanie jako *Processing* lub *Paid*.  
- **Reports (planowane)** – dashboardy Power BI (KPI, wartości brutto/netto, statystyki odrzuceń).  
- **Admin Panel (planowane)** – zarządzanie użytkownikami, źródłami danych i integracjami.  

---

## Role i uprawnienia

- **Administrator** – pełen dostęp do wszystkich modułów.  
- **Reviewer (osoba sprawdzająca)** – dostęp do *Check Invoices* i *Kanban*.  
- **Payments (osoba od płatności)** – dostęp tylko do modułu *Payments*.  

Każdy użytkownik widzi tylko to, co potrzebne – prosto i bezpiecznie.

---

## Automatyzacje

InvoiceIQ wykorzystuje **Power Automate** i **AI Builder**:  
- Power Automate zapisuje nowe faktury (PDF) do SharePoint i uruchamia przepływy.  
- AI Builder OCR odczytuje dane z faktur (nr faktury, dostawca, daty, kwoty).  
- Dane trafiają do **listy SharePoint**, z której korzysta aplikacja.  

---

## Dokumentacja

- [Pełna dokumentacja (PDF)](./docs/InvoiceIQ_Dokumentacja.pdf)  
- [Schemat procesu (PNG)](./assets/diagram.png)  

---

## Roadmapa

- Skanowanie faktur telefonem (OCR).  
- Alerty o nowych fakturach i terminach płatności.  
- Dashboardy Power BI.  
- Integracje z systemami księgowymi i bankowymi.  

---

## Status

- **v1.0** – pierwsze wydanie: Check Invoices, Kanban, Payments, OCR + automatyzacja.  
- Kolejne: Reports + Admin Panel.  
