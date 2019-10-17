import requests
from bs4 import BeautifulSoup
import sqlite3
import re

db = sqlite3.connect("un.db")
cursor = db.cursor()

cursor.executescript(
    """
DROP TABLE IF EXISTS Countries;
DROP TABLE IF EXISTS GeneralInfo;
DROP TABLE IF EXISTS EconIndicator;
"""
)

cursor.execute(
    """
CREATE TABLE Countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    link TEXT
)
"""
)

cursor.execute(
    """
    CREATE TABLE GeneralInfo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id INTEGER,
        region TEXT,
        membership_date TEXT,
        population INTEGER,
        surface_area INTEGER,
        density REAL,
        sex_ratio REAL,
        capital TEXT,
        currency TEXT,
        capital_population REAL,
        exchange_rate REAL
    )
    """
)

cursor.execute(
    """
    CREATE TABLE EconIndicator (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id INTEGER,
        year INTEGER,
        GDP INTEGER,
        GDP_growth REAL,
        GDP_per_capita REAL,
        agriculture REAL,
        industry REAL,
        services REAL,
        employ_agriculture REAL,
        employ_industry REAL,
        employ_services REAL,
        unemployment REAL,
        participation_rate_female REAL,
        participation_rate_male REAL,
        CPI INTEGER,
        agriculture_index INTEGER,
        exports INTEGER,
        imports INTEGER,
        trade_balance INTEGER,
        current_account INTEGER
    )
    """
)


BASE_URL = "http://data.un.org/"


def find_country_link(db):

    html = requests.get(BASE_URL).text
    parsed_html = BeautifulSoup(html, "html.parser")
    countries = parsed_html.find_all(class_="CountryList")[0]
    country_links = countries.find_all("a")

    for country in country_links:
        name = country.text
        link = country["href"]

        db.cursor().execute(
            """
            INSERT INTO Countries (name, link) VALUES (?, ?)
        """,
            (name, link),
        )

    db.commit()


def extract_country(country_id, country_name, country_link, db):
    page_url = BASE_URL + country_link
    html = requests.get(page_url).text
    parsed_html = BeautifulSoup(html, "html.parser")

    tables = parsed_html.find_all("details")
    print(len(tables))
    general_information_table = tables[0]

    economic_table = tables[1]

    # extract_general_information(general_information_table, country_id, db)
    extract_economic_indicators(economic_table, country_id, db)
    db.commit()


def extract_general_information(table, country_id, db):
    table_name = table.summary.text
    rows = table.find_all("tr")
    info_dict = dict()

    for row in rows:
        cells = row.find_all("td")
        field = cells[0].text.replace("\xa0", "")
        value = cells[2].text.replace("\xa0", "")
        if re.search("\d+\s?\.?\d+[a-z]", value):
            value = value[:-1]
        info_dict[field] = value

    sql_stmt = """
        INSERT INTO GeneralInfo (country_id, region, membership_date, population, surface_area, density, sex_ratio, capital, currency, capital_population, exchange_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    region = info_dict["Region"]
    membership_date = info_dict["UN membership date"]

    pre_population = info_dict["Population(000, 2018)"].replace(" ", "")
    population = int(pre_population)

    pre_surface_area = info_dict["Surface area(km2)"].replace(" ", "")
    surface_area = int(pre_surface_area)

    pre_density = info_dict["Pop. density(per km2, 2018)"].replace(" ", "")
    density = float(pre_density)

    pre_sex_ratio = info_dict["Sex ratio(m per 100 f)"].replace(" ", "")
    sex_ratio = float(pre_sex_ratio)

    capital = info_dict["Capital city"]
    currency = info_dict["National currency"]

    pre_capital_population = info_dict["Capital city pop.(000, 2018)"].replace(" ", "")
    capital_population = float(pre_capital_population)

    pre_exchange_rate = info_dict["Exchange rate(per US$)"].replace(" ", "")
    exchange_rate = float(pre_exchange_rate)

    db.cursor().execute(
        sql_stmt,
        (
            country_id,
            region,
            membership_date,
            population,
            surface_area,
            density,
            sex_ratio,
            capital,
            currency,
            capital_population,
            exchange_rate,
        ),
    )


def extract_economic_indicators(table, country_id, db):
    # Problem in agriculture index
    table_name = table.summary.text
    rows = table.find_all("tr")[1:]

    econ_dict = {"2005": {}, "2010": {}, "2018": {}}

    for row in rows:
        cells = row.find_all("td")
        cell_name = cells[0].text.replace("\xa0", "")

        year_2005 = remove_trailing_chars(cells[1].text)
        year_2010 = remove_trailing_chars(cells[2].text)
        year_2018 = remove_trailing_chars(cells[3].text)

        year_2005 = format_value(year_2005)
        year_2010 = format_value(year_2010)
        year_2018 = format_value(year_2018)

        econ_dict["2005"].update({cell_name: year_2005})
        econ_dict["2010"].update({cell_name: year_2010})
        econ_dict["2018"].update({cell_name: year_2018})

    for year in econ_dict.keys():
        data = econ_dict[year]
        yearly_data = flatten_tuple(data.values())
        yearly_data = (country_id, int(year), *yearly_data)

        db.cursor().execute(
            """
            INSERT INTO EconIndicator (country_id, year, GDP, GDP_growth, GDP_per_capita, agriculture, industry, services, employ_agriculture, employ_industry, employ_services, unemployment, participation_rate_female, participation_rate_male, CPI, agriculture, exports, imports, trade_balance, current_account) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            yearly_data,
        )

    # """
    #     CREATE TABLE EconIndicator (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         country_id INTEGER,
    #         GDP INTEGER,
    #         GDP_growth REAL,
    #         GDP_per_capita REAL,
    #         agriculture REAL,
    #         industry REAL,
    #         services REAL,
    #         employ_agriculture REAL,
    #         employ_industry REAL,
    #         employ_services REAL,
    #         unemployment REAL,
    #         participation_rate_female REAL,
    #         participation_rate_male REAL,
    #         CPI INTEGER,
    #         agriculture_index INTEGER,
    #         exports INTEGER,
    #         imports INTEGER,
    #         trade_balance INTEGER,
    #         current_account INTEGER
    #     )
    #     """


def format_value(number):
    number = number.strip()
    if number == "...":
        return None
    if re.search("\d+\.?\d+\s?/\s*\d+\.?\d+", number):
        female, male = number.split("/")
        return (float(female.strip()), float(male.strip()))
    if re.search("-?\s?\d+\.\d+$", number):
        number = number.replace(" ", "")
        return float(number)
    number = number.replace(" ", "")
    return int(number)


def remove_trailing_chars(value):
    m = re.search("\d+\s?\.?\d+([a-z,]+)", value)
    if m:
        value = value.replace(m.group(1), "")
        return value
    return value


def flatten_tuple(values):
    expanded_list = []
    for el in values:
        if isinstance(el, tuple):
            expanded_list = expanded_list + [*el]
        else:
            expanded_list.append(el)
    return expanded_list


extract_country(1, "AF", "en/iso/af.html", db)

