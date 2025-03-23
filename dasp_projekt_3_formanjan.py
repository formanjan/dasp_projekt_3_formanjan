"""
dasp_projekt_3_formanjan.py: Datový analytik s Pythonem - Projekt 3

author: Jan Forman
email: formanjan@seznam.cz
discord: janforman
"""

import sys  # Načtou se argumenty z příkazové řádky
import requests  # Načte se HTML stránka přes HTTP požadavek
from bs4 import BeautifulSoup  # HTML se zpracuje pomocí knihovny BeautifulSoup
import csv  # Výsledky se uloží do CSV souboru
import os  # Zjistí se absolutní cesta k výstupnímu souboru
from datetime import datetime  # Získá se aktuální datum a čas

log_lines = []  # Inicializuje se seznam pro uchování zpráv z běhu skriptu
start_time = datetime.now()  # Uloží se čas spuštění skriptu

def log(message):  # Definuje se funkce pro logování zpráv
    """
    Vypíše zprávu do terminálu a zároveň ji uloží do seznamu pro pozdější zápis do protokolu.
    """
    print(message)  # Zpráva se vypíše do terminálu
    log_lines.append(message)  # Zpráva se uloží do seznamu

def zkontroluj_argumenty():
    """
    Zkontroluje, zda byly zadány dva argumenty – URL a název CSV souboru.
    Pokud ne, ukončí skript a zobrazí nápovědu.
    """
    if len(sys.argv) != 3:  # Ověří se počet argumentů
        log("********************************************************************************************************************************")
        log("Ups, něco se pokazilo: Skript očekává 2 argumenty – URL kraje (dej jej do uvozovek) a název výstupního CSV souboru vč. koncovky.")
        log('Příklad spuštění: python projekt_3.py "https://www.volby.cz/" vysledky.csv')
        log("********************************************************************************************************************************")
        sys.exit(1)  # Skript se ukončí
    return sys.argv[1], sys.argv[2]  # Vrátí se URL a název výstupního souboru

def zkontroluj_url(url):
    """
    Zkontroluje, že zadaná URL začíná správným prefixem.
    """
    if not url.startswith("https://www.volby.cz/pls/ps2017nss/ps32"):  # Zkontroluje se začátek odkazu
        log("Chybný formát odkazu. Zkontroluj, že začíná správně (ps3.. územní celky – výběr územní úrovně).")
        sys.exit(1)  # Skript se ukončí

def stahni_html(url):
    """
    Stáhne HTML obsah z dané URL adresy. Pokud dojde k chybě, skript se ukončí.
    Vrací: objekt BeautifulSoup s HTML obsahem.
    """
    response = requests.get(url)  # Odesílá se GET požadavek
    if response.status_code != 200:  # Ověří se úspěšnost požadavku
        log(f"Chyba: Nepodařilo se načíst stránku. HTTP status code: {response.status_code}")
        sys.exit(1)  # Skript se ukončí
    return BeautifulSoup(response.text, 'html.parser')  # HTML se naparsuje pomocí BeautifulSoup

def ziskej_odkazy_na_obce(soup):
    """
    Najde všechny tabulky obcí na stránce a z nich vytáhne (kód, název, odkaz na detail).
    Vrací: seznam trojic (code, name, full_url).
    """
    obec_links = []  # Inicializuje se prázdný seznam pro odkazy
    base_url = "https://www.volby.cz/pls/ps2017nss/"  # Nastaví se základní URL
    tables = soup.find_all('table', class_='table')  # Vyhledají se všechny tabulky obcí

    for table in tables:  # Projde se každá tabulka
        rows = table.find_all('tr')[2:]  # Přeskočí se hlavička tabulky

        for row in rows:  # Projde se každý řádek v tabulce
            cells = row.find_all('td')  # Najdou se buňky v řádku
            if len(cells) < 3:  # Ověří se, že jich je dostatek
                continue  # Řádek se přeskočí

            code = cells[0].text.strip()  # Získá se kód obce
            name = cells[1].text.strip()  # Získá se název obce
            link_cell = cells[2].find('a')  # Najde se odkaz

            if link_cell and 'href' in link_cell.attrs:  # Ověří se, že odkaz existuje
                relative_link = link_cell['href']  # Získá se relativní odkaz
                full_link = base_url + relative_link  # Spojí se s base URL
                obec_links.append((code, name, full_link))  # Odkaz se přidá do seznamu

    return obec_links  # Vrátí se seznam obcí

def ziskej_vysledky_pro_obec(code, name, link, sorted_party_names):
    """
    Stáhne a zpracuje výsledky voleb pro jednu obec.
    Vrací:
        - list s daty o obci (nebo None, pokud obec nemá statistiky),
        - seznam názvů stran (setříděný), pouze pokud byl prázdný.
    """
    log(f"Zpracovávám obec: {name} ({code})")  # Vypíše se info o obci
    response = requests.get(link)  # Načte se HTML stránky obce
    soup = BeautifulSoup(response.text, 'html.parser')  # HTML se zpracuje

    stats_table = soup.find_all('table')[0]  # Najde se první tabulka se statistikami
    stats_cells = stats_table.find_all('td')  # Najdou se buňky tabulky

    if len(stats_cells) < 8:  # Zkontroluje se dostatečný počet údajů
        log(f"⚠️ U obce {name} ({code}) chybí statistiky, přeskočeno.")  # Vypíše se varování
        return None, sorted_party_names  # Obec se přeskočí

    registered = stats_cells[3].text.replace('\xa0', '').replace(' ', '')  # Získá se počet registrovaných voličů
    envelopes = stats_cells[4].text.replace('\xa0', '').replace(' ', '')  # Získá se počet vydaných obálek
    valid = stats_cells[7].text.replace('\xa0', '').replace(' ', '')  # Získá se počet platných hlasů

    vote_tables = soup.find_all('table')[1:]  # Najdou se všechny další tabulky s hlasy
    parties = {}  # Inicializuje se slovník pro hlasy stran

    for table in vote_tables:  # Projde se každá tabulka
        rows = table.find_all('tr')[2:]  # Přeskočí se hlavička tabulky

        for row in rows:  # Projde se každý řádek
            cells = row.find_all('td')  # Najdou se buňky
            if len(cells) >= 2:  # Zkontroluje se minimální počet buněk
                party_name = cells[1].text.strip()  # Získá se název strany
                vote_count = cells[2].text.strip().replace('\xa0', '').replace(' ', '').replace('-',
                                                                                                '0')  # Získá počet hlasů a nahradí pomlčky nulou (problém s testovacími samples viz Jeseník)
                parties[party_name] = vote_count  # Uloží se do slovníku

    if not sorted_party_names:  # Pokud nejsou názvy stran zatím uloženy
        sorted_party_names = sorted(parties.keys())  # Seřadí se názvy stran

    # Vypočítá se součet hlasů všech stran
    soucet_hlasu = sum(int(parties.get(party, '0')) for party in sorted_party_names)

    # Kontrola na neplausibilní statistiky
    if int(valid) > int(registered) and soucet_hlasu == 0:
        log(f"⚠️ U obce {name} ({code}) byla zjištěna neplausibilní statistika – přeskočeno.")
        return None, sorted_party_names

    votes = [parties.get(party, '0') for party in sorted_party_names]  # Vytvoří se seznam hlasů ve správném pořadí
    return [code, name, registered, envelopes, valid] + votes, sorted_party_names  # Vrátí se výsledkový řádek



def uloz_do_csv(output_filename, header, data):
    """
    Uloží výsledky do CSV souboru.
    Vrací: absolutní cestu k uloženému CSV souboru.
    """
    with open(output_filename, mode='w', newline='', encoding='utf-8-sig') as file:  # Otevře se CSV soubor pro zápis
        writer = csv.writer(file, delimiter=';')  # Vytvoří se writer objekt
        writer.writerow(header)  # Zapíše se hlavička
        writer.writerows(data)  # Zapíšou se řádky s daty
    full_path = os.path.abspath(output_filename)  # Získá se absolutní cesta
    log(f"\n✅ Hotovo! Výsledky byly uloženy do souboru:\n{full_path}")  # Vypíše se zpráva o uložení
    return full_path  # Vrátí se cesta k souboru

def uloz_protokol(output_filename, url, celkem, uspesne, chyby, csv_cesta):
    """
    Uloží protokol (zprávy z terminálu) do textového souboru a zobrazí přehled.
    """
    end_time = datetime.now()  # Získá se čas ukončení
    cas_behu = end_time - start_time  # Spočítá se délka běhu

    log("\n📄 PROTOKOL BĚHU SKRIPTU")  # Vypíše se hlavička protokolu
    log(f"🕒 Čas spuštění: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")  # Vypíše se začátek
    log(f"🕓 Čas dokončení: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")  # Vypíše se konec
    log(f"⌛ Celkový čas běhu: {cas_behu}")  # Vypíše se délka běhu
    log(f"🌐 Zadaná URL adresa: {url}")  # Vypíše se URL
    log(f"📊 Obcí celkem: {celkem}")  # Vypíše se počet obcí
    log(f"✅ Úspěšně zpracováno: {uspesne}")  # Vypíše se počet úspěšných
    log(f"⚠️ Přeskočeno kvůli chybě: {chyby}")  # Vypíše se počet přeskočených
    log(f"📁 Uložený soubor: {csv_cesta}")  # Vypíše se cesta k CSV

    log_filename = output_filename.replace('.csv', '_protokol.txt')  # Vytvoří se název protokolu
    with open(log_filename, mode='w', encoding='utf-8') as log_file:  # Otevře se soubor pro zápis
        log_file.write('\n'.join(log_lines))  # Zapíše se celý log
    log(f"📄 Protokol uložen jako: {os.path.abspath(log_filename)}")  # Vypíše se info o protokolu

def main():
    """
    Hlavní funkce – spouští jednotlivé části skriptu.
    """
    url, output_filename = zkontroluj_argumenty()  # Načtou se argumenty
    zkontroluj_url(url)  # Ověří se URL
    soup = stahni_html(url)  # Stáhne se HTML
    obec_links = ziskej_odkazy_na_obce(soup)  # Získají se odkazy na obce

    vysledky = []  # Inicializuje se seznam výsledků
    sorted_party_names = []  # Inicializuje se seznam stran
    chyby = 0  # Nastaví se počítadlo chyb

    for code, name, link in obec_links:  # Projde se každá obec
        row, sorted_party_names = ziskej_vysledky_pro_obec(code, name, link, sorted_party_names)  # Získají se výsledky
        if row:  # Pokud je řádek platný
            vysledky.append(row)  # Přidá se do výsledků
        else:
            chyby += 1  # Zvýší se počet chyb

    header = ['code', 'location', 'registered', 'envelopes', 'valid'] + sorted_party_names  # Vytvoří se hlavička CSV
    csv_cesta = uloz_do_csv(output_filename, header, vysledky)  # Uloží se do CSV
    uloz_protokol(output_filename, url, len(obec_links), len(vysledky), chyby, csv_cesta)  # Vytvoří se protokol

if __name__ == "__main__":  # Spustí se hlavní funkce, pokud se soubor spustí napřímo
    main()
