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
    db.create_table()


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

    # extraction_list = {
    #     "General Information": extract_general_information,
    #     "Economic indicators": extract_economic_indicators,
    #     "Social indicators": extract_social_indicators,
    #     "Environment and infrastructure indicators": extract_env_indicators,
    # }

    for table in tables:
        if table.summary.text == "General Information":
            extract_general_information(table, country_id, db)
        # elif table.summary.text == "Social indicators":
        #     extract_economic_indicators(table, country_id, db)
        # elif table.summary.text == "Economic indicators":
        #     extract_social_indicators(table, country_id, db)
        # elif table.summary.text == "Environment and infrastructure indicators":
        #     extract_env_indicators(table, country_id, db)


def extract_general_information(table, country_id, db):
    table_name = table.summary.text
    rows = table.find_all("tr")
    info_dict = dict()

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

    for row in rows:
        cells = row.find_all("td")
        field = cells[0].text.replace("\xa0", "")
        cleaned_field = clean_general_information_header(field)
        value = cells[2].text.replace("\xa0", "")
        if re.search("\d+\s?\.?\d+[a-z]", value):
            value = value[:-1]
        info_dict[cleaned_field] = value

    cleaned_dict = {k: None for k in headings}

    p.pprint(info_dict)

    for key in cleaned_dict:
        print(key)
        cleaned_dict[key] = format_value(info_dict.get(key, None))

    p.pprint(info_dict)

    sql_stmt = """
        INSERT INTO GeneralInfo (country_id, region, membership_date, population, surface_area, density, sex_ratio, capital, currency, capital_population, exchange_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # region = info_dict["Region"]
    # membership_date = info_dict["UN membership date"]

    # pre_population = info_dict["Population(000, 2018)"].replace(" ", "")
    # population = int(pre_population)

    # pre_surface_area = info_dict["Surface area(km2)"].replace(" ", "")
    # surface_area = int(pre_surface_area)

    # pre_density = info_dict["Pop. density(per km2, 2018)"].replace(" ", "")
    # density = float(pre_density)

    # pre_sex_ratio = info_dict["Sex ratio(m per 100 f)"].replace(" ", "")
    # sex_ratio = float(pre_sex_ratio)

    # capital = info_dict["Capital city"]
    # currency = info_dict["National currency"]

    # pre_capital_population = info_dict["Capital city pop.(000, 2018)"].replace(" ", "")
    # capital_population = float(pre_capital_population)

    # pre_exchange_rate = info_dict["Exchange rate(per US$)"].replace(" ", "")
    # exchange_rate = float(pre_exchange_rate)

    db.cursor.execute(
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

    db.conn.commit()


def extract_economic_indicators(table, country_id, db):
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

        # print(econ_dict)

    for year in econ_dict.keys():
        data = econ_dict[year]
        yearly_data = flatten_tuple(data.values())
        yearly_data = (country_id, int(year), *yearly_data)
        if not len(yearly_data) == 21:
            yearly_data = (*yearly_data, None)

        print("Econ Indicator: ")
        print(yearly_data)

        db.cursor.execute(
            """
            INSERT INTO EconIndicator (country_id, year, GDP, GDP_growth, GDP_per_capita, agriculture, industry, services, employ_agriculture, employ_industry, employ_services, unemployment, participation_rate_female, participation_rate_male, CPI, agriculture_index, exports, imports, trade_balance, current_account, industrial_index) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?)
            """,
            yearly_data,
        )

    db.conn.commit()


def extract_social_indicators(table, country_id, db):
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

        print("Social Indicator: ")
        print(yearly_data)

        db.cursor.execute(
            """
            INSERT INTO SocialIndicator (
                country_id, year, population_growth, urban_population, urban_population_growth,fertility_rate, life_expectancy_females, life_expectancy_males, population_distribution_children, population_distribution_adults, migrant, migrant_ratio, refugees, infant_mortality, health_expenditure, physicians_ratio, education_expenditure, primary_enroll_ratio_females, primary_enroll_ratio_males, secondary_enroll_ratio_females, secondary_enroll_ratio_males, tertiary_enroll_ratio_females, tertiary_enroll_ratio_males, homicide_rate, women_in_parliaments
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?
            )
            """,
            yearly_data,
        )

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
# countries = db.cursor.execute(
#     """
#     SELECT id, name, link FROM Countries LIMIT 5
#     """
# )

# for country in countries.fetchall():
#     print(country)
#     extract_country(*country, db)
extract_country(1, "AF", "en/iso/af.html", db)

db.conn.commit()

