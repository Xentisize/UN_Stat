import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from utils import *
from database import DataBaseManagement

DEBUG = True
db = DataBaseManagement("./test.db")

if DEBUG:
    import pprint

    p = pprint.PrettyPrinter(indent=4)
    db.drop_tables()
    db.create_table(table="econ")


BASE_URL = "http://data.un.org/"


def find_country_link(db):

    html = requests.get(BASE_URL).text
    parsed_html = BeautifulSoup(html, "html.parser")
    countries = parsed_html.find_all(class_="CountryList")[0]
    country_links = countries.find_all("a")

    for country in country_links[:5]:
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
            # extract_general_information(table, country_id, db)
            pass
        elif table.summary.text == "Social indicators":
            pass
            # extract_social_indicators(table, country_id, db)
        elif table.summary.text == "Economic indicators":
            extract_economic_indicators(table, country_id, db)
        # elif table.summary.text == "Environment and infrastructure indicators":
        #     extract_env_indicators(table, country_id, db)


def extract_general_information(table, country_id, db):
    table_name = table.summary.text
    rows = table.find_all("tr")
    info_dict = dict()

    for row in rows:
        cells = row.find_all("td")
        field = cells[0].text.replace("\xa0", "")
        cleaned_field = clean_general_information_header(field)
        value = cells[2].text.replace("\xa0", "")
        if re.search("\d+\s?\.?\d+[a-z]", value):
            value = value[:-1]
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

    p.pprint(econ_dict["2005"])

    for year in ["2005", "2010", "2018"]:
        if econ_dict[year]["Labour participation (females)"]:
            females, males = econ_dict[year]["Labour participation (females)"]
            econ_dict[year]["Labour participation (females)"] = females
            econ_dict[year]["Labour participation (males)"] = males

        econ_dict[year]["year"] = year
        econ_dict[year]["country_id"] = country_id

    p.pprint(econ_dict["2005"])

    for year in ["2005", "2010", "2018"]:
        table_fields_stmt = ", ".join([f'"{key}"' for key in econ_dict[year].keys()])
        placement_stmt = ", ".join("?" * len(econ_dict[year]))
        table_values_tuples = tuple([val for val in econ_dict[year].values()])

        print("\n\nSQL Statement:")
        print(table_fields_stmt, "\n")
        print(placement_stmt, "\n")

        stmt = "INSERT INTO EconIndicator ( %s ) VALUES ( %s )" % (
            table_fields_stmt,
            placement_stmt,
        )

        print("\n\n", stmt)

        db.cursor.execute(stmt, table_values_tuples)

    # for year in econ_dict.keys():
    #     data = econ_dict[year]
    #     yearly_data = flatten_tuple(data.values())
    #     yearly_data = (country_id, int(year), *yearly_data)
    #     if not len(yearly_data) == 21:
    #         yearly_data = (*yearly_data, None)

    #     print("Econ Indicator: ")
    #     print(yearly_data)

    # db.cursor.execute(
    #     """
    #     INSERT INTO EconIndicator (country_id, year, GDP, GDP_growth, GDP_per_capita, agriculture, industry, services, employ_agriculture, employ_industry, employ_services, unemployment, participation_rate_female, participation_rate_male, CPI, agriculture_index, exports, imports, trade_balance, current_account, industrial_index) VALUES (
    #         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    #         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    #         ?)
    #     """,
    #     yearly_data,
    # )

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
        cleaned_cell_name = clean_social_indicator_header(cell_name)

        year_2005 = remove_trailing_chars(cells[1].text)
        year_2010 = remove_trailing_chars(cells[2].text)
        year_2018 = remove_trailing_chars(cells[3].text)

        year_2005 = format_value(year_2005)
        year_2010 = format_value(year_2010)
        year_2018 = format_value(year_2018)

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

        # commented after testing. need checking
        # social_dict[year][lem] = None
        # social_dict[year][pde] = None
        # social_dict[year][perm] = None
        # social_dict[year][serm] = None
        # social_dict[year][term] = None
        # social_dict[year][mr] = None

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

        print("\n\nSQL Statement:")
        print(table_fields_stmt, "\n")
        print(placement_stmt, "\n")

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

    social_dict = {"2005": {}, "2010": {}, "2018": {}}

    for row in rows:
        cells = row.find_all("td")
        cell_name = cells[0].text.replace("\xa0", "")

        year_2005 = remove_trailing_chars(cells[1].text)
        year_2010 = remove_trailing_chars(cells[2].text)
        year_2018 = remove_trailing_chars(cells[3].text)

        year_2005 = format_value(year_2005)
        year_2010 = format_value(year_2010)
        year_2018 = format_value(year_2018)

        social_dict["2005"].update({cell_name: year_2005})
        social_dict["2010"].update({cell_name: year_2010})
        social_dict["2018"].update({cell_name: year_2018})

    for year in social_dict.keys():
        data = social_dict[year]
        yearly_data = flatten_tuple(data.values())
        yearly_data = (country_id, int(year), *yearly_data)

        print("Env Indicator: ")
        print(yearly_data)

        db.cursor.execute(
            """
            INSERT INTO EnvIndicator (
                country_id, year, internet_individual, threatened_species, forested_area, carbon_dioxide_emission, carbon_dioxide_emission_per_capita, energy_production, energy_supply, protected_sites_ratio, drinking_water_urban, drinking_water_rural, sanitation_urban, sanitation_rural, assistance_received
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
        """,
            yearly_data,
        )
    db.conn.commit()


# find_country_link(db)
countries = db.cursor.execute(
    """
    SELECT id, name, link FROM Countries LIMIT 5
    """
)

for country in countries.fetchall():
    print(country)
    print("Extracting country")
    extract_country(*country, db)
# extract_country(1, "AS", "en/iso/as.html", db)

db.conn.commit()

