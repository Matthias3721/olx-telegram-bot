# OLX Telegram Bot

Inteligentny bot w Pythonie, który **automatycznie monitoruje ogłoszenia OLX** (np. iPhone) i wysyła powiadomienia o nowych okazjach na Telegram.  
Działa **nieprzerwanie 24/7 na serwerze VPS** i w czasie rzeczywistym informuje o nowych ofertach z OLX API.

---

## Opis projektu

Projekt napisany w języku **Python**, oparty na bibliotece [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) oraz oficjalnym **API OLX**.  
Jego głównym zadaniem jest automatyczne monitorowanie ofert sprzedaży i natychmiastowe powiadamianie użytkownika o nowych, atrakcyjnych ogłoszeniach.

Bot analizuje tytuł, cenę, lokalizację i oblicza różnicę względem Twojej docelowej wartości (np. kupna iPhone’a w określonej cenie).  
Wiadomości wysyłane są bezpośrednio do użytkownika Telegrama, z uwzględnieniem zdjęcia, lokalizacji i koloru wskazującego, czy cena jest wyższa (🟥) czy niższa (🟩) od docelowej.

---

## Kluczowe funkcje

- Pobiera oferty z OLX poprzez API (kategoria, słowo kluczowe, filtr czasu)  
- Wysyła powiadomienia w Telegramie z tytułem, ceną, lokalizacją i linkiem  
- Porównuje cenę z listą docelowych wartości (`PRICES`)  
- Działa cyklicznie — domyślnie co 15 sekund  
- Pamięta, które ogłoszenia już wysłał (unikalny ID oferty)  
- Ignoruje ogłoszenia starsze niż 15 minut  
- Uruchomiony jako **usługa systemowa (`systemd`)** — działa 24/7  
- Funkcjonuje niezależnie w sieci — nawet po restarcie serwera  

---

## Technologia

- **Python 3.8+**
- **Biblioteki:**  
  - `python-telegram-bot` – komunikacja z Telegram API  
  - `requests` – zapytania HTTP do OLX API  
  - `nest_asyncio` – współpraca asynchroniczna w pętli zdarzeń  
- **Środowisko:** Linux (Oracle Cloud VPS)  
- **Tryb działania:** systemd (usługa działająca w tle, restartująca się automatycznie)

---


## Działanie

1. Bot co określony czas (domyślnie 15 sekund) pobiera najnowsze oferty OLX.  
2. Filtruje je według tytułu (np. „iPhone 13 Pro Max”) i porównuje z cennikiem `PRICES`.  
3. Jeśli znajdzie nową ofertę — wysyła wiadomość w Telegramie z:
   - nazwą ogłoszenia,  
   - ceną i różnicą względem docelowej,  
   - lokalizacją,  
   - linkiem do oferty,  
   - oraz pierwszym zdjęciem produktu.  
4. Wszystko odbywa się **w czasie rzeczywistym**, bez potrzeby ręcznej obsługi.

---

## Przykładowe powiadomienie (Telegram)

iPhone 13 Pro Max 256GB
Cena: 1700 zł (🟩 -700)
Link: https://www.olx.pl/d/oferta/iphone-13-pro-max
📍 Lokalizacja: Kraków, Małopolskie

---

## Działanie 24/7

Bot działa jako usługa systemowa `systemd` na serwerze Linux (Oracle Cloud).  
Dzięki temu:
- uruchamia się automatycznie po restarcie serwera,  
- monitoruje OLX nieprzerwanie,  
- sam wznawia działanie w razie błędu.  

Fragment konfiguracji:
[Service]
ExecStart=/home/opc/telegram_bot/venv38/bin/python /home/opc/telegram_bot/bot_olx.py
Restart=always


---

## Zależności

Plik `requirements.txt`:
```txt
requests>=2.31
python-telegram-bot>=20,<22
nest_asyncio>=1.6

---

## Możliwości rozwoju
Dodanie integracji z innymi kategoriami OLX (np. samochody, laptopy)

Zmiana słowa kluczowego z „iphone” na dowolny produkt

Ulepszony system powiadomień (np. e-mail lub webhook)

Wykresy i statystyki cen (np. przez Google Sheets lub Grafanę)

Frontend webowy do konfiguracji botów

Autor:
Matthias3721

Projekt stworzony jako praktyczny przykład automatyzacji analizy ofert w Pythonie.
Bot działa w środowisku produkcyjnym od 2025 r. – całkowicie autonomicznie i w pełni funkcjonalnie.
