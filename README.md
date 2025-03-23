# dasp_projekt_3_formanjan
# Projekt 3 – Volební výsledky do CSV (Engeto Python Akademie)

Tento Python skript umožňuje stáhnout výsledky voleb z webu [volby.cz](https://www.volby.cz) pro konkrétní územní celek a uložit je do CSV souboru včetně automatického vytvoření textového protokolu o běhu skriptu.

---

## Zadání

- Vstupem je **URL adresa** jedné ze stránek s výpisem obcí pro konkrétní kraj z voleb do Poslanecké sněmovny ČR v roce 2017 (např. "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103").
- Druhým vstupem je **název výstupního souboru** ve formátu CSV.
- Výstupem je:
  - CSV soubor obsahující výsledky voleb po jednotlivých obcích,
  - protokol ".txt" shrnující průběh skriptu (čas, URL, počet zpracovaných obcí apod.).

---

## Co skript dělá

1. Zkontroluje, že byly zadány 2 argumenty – URL a název souboru.
2. Ověří správnost URL adresy.
3. Stáhne HTML stránku a najde odkazy na jednotlivé obce.
4. Z každé obce stáhne:
   - počet registrovaných voličů,
   - vydané obálky,
   - platné hlasy,
   - hlasy pro jednotlivé strany.
5. Uloží vše do CSV souboru ve formátu vhodném pro český Excel.
6. Zapíše přehled běhu do protokolového ".txt" souboru.

---

## Jak skript spustit

Skript se spouští z příkazové řádky se dvěma argumenty:

Terminál: python dasp_projekt_3_formanjan.py "URL_KRAJE" nazev_souboru.csv

---

## Jak nainstalovat knihovny třetích stran
- Terminál: pip install requests
- Terminál: pip install beautifulsoup4

---

## Standardizovaný výstup
Pokud se ve standardizovaném výstupu objeví sloupec s pomlčkou, s největší pravděpodobností byla v HTML na úrovni územního celku rozpadajícího se na více okrsků testovací tabulka, která přinášel neplausibilitu dat. Územní celek není vpušten do výstupu, pokud počet platných hlasů převyšuje počet registrovaných a součet hlasů jednotlivých stran je nula.
Sloupec "-" reprezentuje stranu bez uvedeného jména a je ponechán z důvodu možné chyby ve statistických výkaze, kde by nebyla strana specifikována, ale měla uvedena počet hlasů. Z toho důvodu je tento sloupec ponechán jako přípustný. Pokud obsahuje pouze nulové hodnoty, bude se jednat o následech, že některý z územních celků obsahoval testovací tabulky.


---

## Spuštění - ukázky

### Upozornění při nezadání parametrů
- ![obrazek](https://github.com/user-attachments/assets/36a41fa2-f787-4349-86be-7ea05e95db42)

### Spuštění s parametry
- Zadání
- ![obrazek](https://github.com/user-attachments/assets/09e062b0-9115-411a-a964-9890bf66f8ef)

- Dogenerování
- ![obrazek](https://github.com/user-attachments/assets/7aa9d82d-2f6e-46b6-8a04-8d9e8acb1863)

- Soubory
- ![obrazek](https://github.com/user-attachments/assets/03f7ae55-48d5-4983-8509-dd5ef18e154a)

- Ukázka_csv
- ![obrazek](https://github.com/user-attachments/assets/5b6676ee-0339-4086-bc1c-20230b382145)

- Ukázka_protokol
- ![obrazek](https://github.com/user-attachments/assets/42937343-4631-4a76-b515-43fd6e51161c)






