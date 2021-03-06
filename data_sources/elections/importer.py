# -*- encoding: utf-8 -*-

import os
import gzip
import requests
import xml.etree.ElementTree

from typing import Dict, Tuple, List, Any

POLITICAL_PARTIES = {
    '1': 'Česká strana sociálně demokratická',
    '10': 'Strana soukromníků České republiky',
    '11': 'Křesťanská a demokratická unie - Československá strana lidová',
    '12': 'Volte Pravý Blok-stranu za ODVOLAT.polit.,NÍZKÉ daně,VYROVN.rozp.,MIN.byrokr.,SPRAV.just.,PŘÍMOU demokr. WWW.CIBULKA.NET',
    '13': 'Suverenita - Strana zdravého rozumu',
    '14': 'Aktiv nezávislých občanů',
    '15': 'Strana Práv Občanů ZEMANOVCI',
    '16': 'OBČANÉ 2011',
    '17': 'Úsvit přímé demokracie Tomia Okamury',
    '18': 'Dělnická strana sociální spravedlnosti',
    '19': 'Československá strana socialistická',
    '2': 'Strana svobodných občanů',
    '20': 'ANO 2011',
    '21': 'Komunistická strana Čech a Moravy',
    '22': 'LEV 21 - Národní socialisté',
    '23': 'Strana zelených',
    '24': 'Koruna Česká (monarchistická strana Čech, Moravy a Slezska)',
    '3': 'Česká pirátská strana',
    '4': 'TOP 09',
    '5': 'HLAVU VZHŮRU - volební blok',
    '6': 'Občanská demokratická strana',
    '7': 'Romská demokratická strana',
    '8': 'Klub angažovaných nestraníků',
    '9': 'politické hnutí Změna',
}

NUTS = {
    "CZ0100": "Praha",
    "CZ0201": "Benešov",
    "CZ0202": "Beroun",
    "CZ0203": "Kladno",
    "CZ0204": "Kolín",
    "CZ0205": "Kutná Hora",
    "CZ0206": "Mělník",
    "CZ0207": "Mladá Boleslav",
    "CZ0208": "Nymburk",
    "CZ0209": "Praha-východ",
    "CZ020A": "Praha-západ",
    "CZ020B": "Příbram",
    "CZ020C": "Rakovník",
    "CZ0311": "České Budějovice",
    "CZ0312": "Český Krumlov",
    "CZ0313": "Jindřichův Hradec",
    "CZ0314": "Písek",
    "CZ0315": "Prachatice",
    "CZ0316": "Strakonice",
    "CZ0317": "Tábor",
    "CZ0321": "Domažlice",
    "CZ0322": "Klatovy",
    "CZ0323": "Plzeň-město",
    "CZ0324": "Plzeň-jih",
    "CZ0325": "Plzeň-sever",
    "CZ0326": "Rokycany",
    "CZ0327": "Tachov",
    "CZ0411": "Cheb",
    "CZ0412": "Karlovy Vary",
    "CZ0413": "Sokolov",
    "CZ0421": "Děčín",
    "CZ0422": "Chomutov",
    "CZ0423": "Litoměřice",
    "CZ0424": "Louny",
    "CZ0425": "Most",
    "CZ0426": "Teplice",
    "CZ0427": "Ústí nad Labem",
    "CZ0511": "Česká Lípa",
    "CZ0512": "Jablonec nad Nisou",
    "CZ0513": "Liberec",
    "CZ0514": "Semily",
    "CZ0521": "Hradec Králové",
    "CZ0522": "Jičín",
    "CZ0523": "Náchod",
    "CZ0524": "Rychnov nad Kněžnou",
    "CZ0525": "Trutnov",
    "CZ0531": "Chrudim",
    "CZ0532": "Pardubice",
    "CZ0533": "Svitavy",
    "CZ0534": "Ústí nad Orlicí",
    "CZ0631": "Havlíčkův Brod",
    "CZ0632": "Jihlava",
    "CZ0633": "Pelhřimov",
    "CZ0634": "Třebíč",
    "CZ0635": "Žďár nad Sázavou",
    "CZ0641": "Blansko",
    "CZ0642": "Brno-město",
    "CZ0643": "Brno-venkov",
    "CZ0644": "Břeclav",
    "CZ0645": "Hodonín",
    "CZ0646": "Vyškov",
    "CZ0647": "Znojmo",
    "CZ0711": "Jeseník",
    "CZ0712": "Olomouc",
    "CZ0713": "Prostějov",
    "CZ0714": "Přerov",
    "CZ0715": "Šumperk",
    "CZ0721": "Kroměříž",
    "CZ0722": "Uherské Hradiště",
    "CZ0723": "Vsetín",
    "CZ0724": "Zlín",
    "CZ0801": "Bruntál",
    "CZ0802": "Frýdek-Místek",
    "CZ0803": "Karviná",
    "CZ0804": "Nový Jičín",
    "CZ0805": "Opava",
    "CZ0806": "Ostrava-město"
}


def download_data(nuts: str) -> str:
    """
    Stahne soubor obsahujici vysledky voleb do Poslanecne snemovny v danem NUTS.

    Vrati stazena data.
    """
    print('Stahuji data pro NUTS {}'.format(nuts))
    response = requests.get('https://www.volby.cz/pls/ps2013/vysledky_okres?nuts={}'.format(nuts))
    return response.content


def process_data() -> List[Tuple[int, int, str, int]]:
    """
    Stazene soubory obsahujici data k vysledkum voleb se zpracuji a vygeneruje dict s daty.
    """
    xml_namespaces = {'volby': 'http://www.volby.cz/ps/'}
    response_data = []
    for nuts in NUTS:
        data = download_data(nuts)

        xml_file = xml.etree.ElementTree.fromstring(data)

        # Prahu zpracovavam separatne, protoze je rozdelena na obvody a ja je chci secist
        if nuts == 'CZ0100':
            # Data pro Prahu chceme secist
            prague_municipality_id = '554782'
            prague_data_voters = 0
            prague_data_parties = {}  # {party_id: <suma>}

            for municipality in xml_file.findall('volby:OBEC', xml_namespaces):
                prague_data_voters += int(municipality.find('volby:UCAST', xml_namespaces).get('ZAPSANI_VOLICI'))

                for party in municipality.findall('volby:HLASY_STRANA', xml_namespaces):
                    party_id = party.get('KSTRANA')
                    try:
                        prague_data_parties[party_id] += int(party.get('HLASY'))
                    except KeyError:
                        prague_data_parties[party_id] = int(party.get('HLASY'))

            # Zapisu data
            response_data.append(
                (
                    prague_municipality_id,
                    'voters',
                    'Počet registrovaných voličů',
                    prague_data_voters
                )
            )
            for party_id, value in prague_data_parties.items():
                response_data.append(
                    (
                        prague_municipality_id,
                        party_id,
                        POLITICAL_PARTIES[party_id],
                        value
                    )
                )
        # Zbytek se zpracovava standartne
        else:
            for municipality in xml_file.findall('volby:OBEC', xml_namespaces):
                municipality_id = municipality.get('CIS_OBEC')

                response_data.append(
                    (
                        municipality_id,
                        'voters',
                        'Počet registrovaných voličů',
                        municipality.find('volby:UCAST', xml_namespaces).get('ZAPSANI_VOLICI')
                    )
                )
                for party in municipality.findall('volby:HLASY_STRANA', xml_namespaces):
                    party_id = party.get('KSTRANA')
                    party_name = POLITICAL_PARTIES[party_id]
                    votes = party.get('HLASY')
                    response_data.append(
                        (
                            municipality_id,
                            party_id,
                            party_name,
                            votes
                        )
                    )
    print(len(response_data))
    return response_data


def save_to_dump(table_name: str, data: List[Tuple[int, int, str, int]]) -> None:
    """
    Ulozi data do dumpu.
    """

    gzf = gzip.GzipFile(os.path.join('dump', '{}.sql.gz'.format(table_name)), "w", compresslevel=9)

    gzf.write(bytes('PRAGMA foreign_keys = OFF;\n', 'utf-8'))
    gzf.write(bytes('BEGIN TRANSACTION;\n', 'utf-8'))

    # Obec
    gzf.write(bytes('''CREATE TABLE {}_obec (municipality_id INT, metric_id TEXT, metric TEXT, year INT DEFAULT 2013, value REAL);\n'''.format(table_name), 'utf-8'))

    for item in data:
        gzf.write(bytes('''INSERT INTO {}_obec (municipality_id, metric_id, metric, value) VALUES ('{}', '{}', '{}', '{}');\n'''.format(
            table_name, *item
        ), 'utf-8'))

    gzf.write(bytes('COMMIT;\n', 'utf-8'))


def main():
    data = process_data()
    save_to_dump('elections', data)


if __name__ == '__main__':
    main()
