import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from utils import *
from database import DataBaseManagement
import pprint


db = DataBaseManagement("./un.db")
# db.drop_tables()
# db.create_table()
p = pprint.PrettyPrinter(indent=4)


BASE_URL = "http://data.un.org/"


def find_country_link(db):

    html = requests.get(BASE_URL).text
    parsed_html = BeautifulSoup(html, "html.parser")
    countries = parsed_html.find_all(class_="CountryList")[0]
    country_links = countries.find_all("a")

    for country in country_links:
        name = country.text
        link = country["href"]

        db.cursor.execute(
            """
            INSERT INTO Countries (name, link) VALUES (?, ?)
        """,
            (name, link),
        )

    db.conn.commit()


def extract_country(country_id, country_name, country_link, db):
    page_url = BASE_URL + country_link
    html = requests.get(page_url).text
    parsed_html = BeautifulSoup(html, "html.parser")

    tables = parsed_html.find_all("details")

    for table in tables:
        if table.summary.text == "General Information":
            extract_general_information(table, country_id, db)
            # pass
        elif table.summary.text == "Social indicators":
            # pass
            extract_social_indicators(table, country_id, db)
        elif table.summary.text == "Economic indicators":
            # pass
            extract_economic_indicators(table, country_id, db)
        elif table.summary.text == "Environment and infrastructure indicators":
            extract_env_indicators(table, country_id, db)
            # pass


def extract_general_information(table, country_id, db):
    table_name = table.summary.text
    rows = table.find_all("tr")
    info_dict = dict()

    for row in rows:
        cells = row.find_all("td")
        field = cells[0].text.replace("\xa0", "")
        cleaned_field = clean_general_information_header(field)
        value = cells[2].text.replace("\xa0", "")
        # if re.search("\d+\s?\.?\d+[a-z]", value):
        #     value = value[:-1]
        value = remove_trailing_chars(value)
        info_dict[cleaned_field] = value

    headings = [
        "Region",
        "UN membership date",
        "Population",
        "Population density",
        "Surface area",
        "Sex ratio",
        "Capital city",
        "Capital population",
        "National currency",
        "Exchange rate",
    ]

    cleaned_dict = {k: None for k in headings}

    for key in cleaned_dict:
        cleaned_dict[key] = format_value(info_dict.get(key, None))

    item_tuples = (country_id,) + tuple(value for value in cleaned_dict.values())

    stmt = """
        INSERT INTO GeneralInfo (country_id, region, membership_date, population, population_density, surface_area, sex_ratio, capital_city, capital_population, currency, exchange_rate) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?
        )
    """

    db.cursor.execute(stmt, item_tuples)
    db.conn.commit()


def extract_economic_indicators(table, country_id, db):
    table_name = table.summary.text
    rows = table.find_all("tr")[1:]

    econ_headings = [
        "GDP",
        "GDP growth",
        "GDP per capita",
        "Agriculture",
        "Industry",
        "Services",
        "Agriculture employment",
        "Industry employment",
        "Services employment",
        "Unemployment rate",
        "Labour participation (females)",
        "Labour participation (males)",
        "CPI",
        "Agricultural index",
        "Industrial index",
        "Exports",
        "Imports",
        "Trade balance",
        "Current account",
    ]

    econ_dict = {"2005": {}, "2010": {}, "2018": {}}

    for year in ["2005", "2010", "2018"]:
        for heading in econ_headings:
            econ_dict[year][heading] = None

    for row in rows:
        cells = row.find_all("td")
        cell_name = cells[0].text.replace("\xa0", "")
        cleaned_cell_name = clean_econ_indicator_header(cell_name)

        year_2005 = remove_trailing_chars(cells[1].text)
        year_2010 = remove_trailing_chars(cells[2].text)
        year_2018 = remove_trailing_chars(cells[3].text)

        year_2005 = format_value(year_2005)
        year_2010 = format_value(year_2010)
        year_2018 = format_value(year_2018)

        econ_dict["2005"].update({cleaned_cell_name: year_2005})
        econ_dict["2010"].update({cleaned_cell_name: year_2010})
        econ_dict["2018"].update({cleaned_cell_name: year_2018})

    for year in ["2005", "2010", "2018"]:
        if econ_dict[year]["Labour participation (females)"]:
            females, males = econ_dict[year]["Labour participation (females)"]
            econ_dict[year]["Labour participation (females)"] = females
            econ_dict[year]["Labour participation (males)"] = males

        econ_dict[year]["year"] = year
        econ_dict[year]["country_id"] = country_id

    # p.pprint(econ_dict["2005"])

    for year in ["2005", "2010", "2018"]:
        table_fields_stmt = ", ".join([f'"{key}"' for key in econ_dict[year].keys()])
        placement_stmt = ", ".join("?" * len(econ_dict[year]))
        table_values_tuples = tuple([val for val in econ_dict[year].values()])

        stmt = "INSERT INTO EconIndicator ( %s ) VALUES ( %s )" % (
            table_fields_stmt,
            placement_stmt,
        )

        db.cursor.execute(stmt, table_values_tuples)
        p.pprint(econ_dict["2005"])

    db.conn.commit()


def extract_social_indicators(table, country_id, db):
    table_name = table.summary.text
    rows = table.find_all("tr")[1:]

    social_headings = [
        "country_id",
        "year",
        "Population growth",
        "Urban population",
        "Urban population growth",
        "Fertility rate",
        "Life expectancy (females)",
        "Life expectancy (males)",
        "Population distribution (children)",
        "Population distribution (elders)",
        "Migrant",
        "Migrant ratio",
        "Refugees",
        "Infant mortality",
        "Health expenditure",
        "Physicians ratio",
        "Education expenditure",
        "Primary enroll ratio (females)",
        "Primary enroll ratio (males)",
        "Secondary enroll ratio (females)",
        "Secondary enroll ratio (males)",
        "Tertiary enroll ratio (females)",
        "Tertiary enroll ratio (males)",
        "Homicide rate",
        "Women in parliaments",
    ]

    social_dict = {"2005": {}, "2010": {}, "2018": {}}

    # initialize the dict with all headings
    for year in ["2005", "2010", "2018"]:
        for heading in social_headings:
            social_dict[year][heading] = None

    for row in rows:
        cells = row.find_all("td")
        cell_name = cells[0].text.replace("\xa0", "")
        p.pprint(f'Cell name: {cell_name}')
        cleaned_cell_name = clean_social_indicator_header(cell_name)

        year_2005 = remove_trailing_chars(cells[1].text)
        year_2010 = remove_trailing_chars(cells[2].text)
        year_2018 = remove_trailing_chars(cells[3].text)

        year_2005 = format_value(year_2005)
        year_2010 = format_value(year_2010)
        year_2018 = format_value(year_2018)

        p.pprint(f"{cleaned_cell_name} - {year_2005}")
        p.pprint(f"{cleaned_cell_name} - {year_2010}")

        social_dict["2005"].update({cleaned_cell_name: year_2005})
        social_dict["2010"].update({cleaned_cell_name: year_2010})
        social_dict["2018"].update({cleaned_cell_name: year_2018})

    p.pprint(social_dict["2005"])

    for year in ["2005", "2010", "2018"]:
        # abbreviation for saving some typing in the following dict's key
        lef = "Life expectancy (females)"
        lem = "Life expectancy (males)"
        pdc = "Population distribution (children)"
        pde = "Population distribution (elders)"
        perf = "Primary enroll ratio (females)"
        perm = "Primary enroll ratio (males)"
        serf = "Secondary enroll ratio (females)"
        serm = "Secondary enroll ratio (males)"
        terf = "Tertiary enroll ratio (females)"
        term = "Tertiary enroll ratio (males)"
        m = "Migrant"
        mr = "Migrant ratio"

        if social_dict[year][lef]:
            females, males = social_dict[year][lef]
            social_dict[year][lef] = females
            social_dict[year][lem] = males

        if social_dict[year][pdc]:
            children, elders = social_dict[year][pdc]
            social_dict[year][pdc] = children
            social_dict[year][pde] = elders

        if social_dict[year][perf]:
            females, males = social_dict[year][perf]
            social_dict[year][perf] = females
            social_dict[year][perm] = males

        if social_dict[year][serf]:
            females, males = social_dict[year][serf]
            social_dict[year][serf] = females
            social_dict[year][serm] = males

        if social_dict[year][terf]:
            females, males = social_dict[year][terf]
            social_dict[year][terf] = females
            social_dict[year][term] = males

        if social_dict[year][m]:
            migrant, migrant_ratio = social_dict[year][m]
            social_dict[year][m] = migrant
            social_dict[year][mr] = migrant_ratio

        # add country and year in the dict
        social_dict[year]["year"] = year
        social_dict[year]["country_id"] = country_id

    p.pprint(social_dict["2005"])

    for year in ["2005", "2010", "2018"]:
        table_fields_stmt = ", ".join([f'"{key}"' for key in social_dict[year].keys()])
        placement_stmt = ", ".join("?" * len(social_dict[year]))
        table_values_tuples = tuple([val for val in social_dict[year].values()])

        stmt = "INSERT INTO SocialIndicator ( %s ) VALUES ( %s )" % (
            table_fields_stmt,
            placement_stmt,
        )

        print("\n\n", stmt)

        db.cursor.execute(stmt, table_values_tuples)

    db.conn.commit()


def extract_env_indicators(table, country_id, db):
    table_name = table.summary.text
    rows = table.find_all("tr")[1:]

    env_headings = [
        "Internet usage",
        "Research expenditure",
        "Threatened species",
        "Forested area",
        "CO2 emission",
        "CO2 emission (per capita)",
        "Energy production",
        "Energy supply",
        "Tourists",
        "Important sites",
        "Drinking water (urban)",
        "Drinking water (rural)",
        "Sanitation (urban)",
        "Sanitation (rural)",
        "Assist disbursed",
        "Assist received",
    ]

    env_dict = {"2005": {}, "2010": {}, "2018": {}}

    for year in ["2005", "2010", "2018"]:
        for heading in env_headings:
            env_dict[year][heading] = None

    for row in rows:
        cells = row.find_all("td")
        cell_name = cells[0].text.replace("\xa0", "")
        cleaned_cell_name = clean_env_indicator_header(cell_name)

        year_2005 = remove_trailing_chars(cells[1].text)
        year_2010 = remove_trailing_chars(cells[2].text)
        year_2018 = remove_trailing_chars(cells[3].text)

        year_2005 = format_value(year_2005)
        year_2010 = format_value(year_2010)
        year_2018 = format_value(year_2018)

        env_dict["2005"].update({cleaned_cell_name: year_2005})
        env_dict["2010"].update({cleaned_cell_name: year_2010})
        env_dict["2018"].update({cleaned_cell_name: year_2018})

    p.pprint(env_dict["2005"])

    for year in ["2005", "2010", "2018"]:
        # abbreviation for saving time in typing
        co2 = "CO2 emission"
        co2pc = "CO2 emission (per capita)"
        dwr = "Drinking water (rural)"
        dwu = "Drinking water (urban)"
        sr = "Sanitation (rural)"
        su = "Sanitation (urban)"
        d = env_dict[year]

        if d[co2]:
            emission, emission_per_capita = d[co2]
            d[co2] = emission
            d[co2pc] = emission_per_capita

        if d[dwu]:
            print(d[dwu])
            urban, rural = d[dwu]
            d[dwu] = urban
            d[dwr] = rural

        if d[su]:
            urban, rural = d[su]
            d[su] = urban
            d[sr] = rural

        d["year"] = year
        d["country_id"] = country_id

    for year in ["2005", "2010", "2018"]:
        table_fields_stmt = ", ".join([f'"{key}"' for key in env_dict[year].keys()])
        placement_stmt = ", ".join("?" * len(env_dict[year]))
        table_values_tuples = tuple([val for val in env_dict[year].values()])

        stmt = "INSERT INTO EnvIndicator ( %s ) VALUES ( %s )" % (
            table_fields_stmt,
            placement_stmt,
        )

        print("\n\n", stmt)

        db.cursor.execute(stmt, table_values_tuples)

    db.conn.commit()



db.cursor.execute(
    """
    SELECT country_id FROM GeneralInfo ORDER BY country_id DESC LIMIT 1
    """
)

last_insert_general_info_id = db.cursor.fetchone()[0]
print('Last country_id:', last_insert_general_info_id)

# find_country_link(db)
countries = db.cursor.execute(
    """
    SELECT id, name, link FROM Countries
    """
)


for country in countries.fetchall():
    if country[0] < last_insert_general_info_id:
        continue
    print(country)
    extract_country(*country, db)

# extract_country(7, 'Anguilla', 'en/iso/ai.html', db)

db.conn.commit()

