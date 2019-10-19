import sqlite3


class DataBaseManagement:
    def __init__(self, db="/mnt/s/Downloads/un.sqlite"):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()

    def create_table(self, table="all"):
        table_function = dict()
        table_function["countries"] = self.create_countries_table
        table_function["general"] = self.create_general_table
        table_function["econ"] = self.create_econ_table
        table_function["social"] = self.create_social_table
        table_function["environment"] = self.create_environment_table

        if table == "all":
            for func in table_function.values():
                func()
        elif table == "countries":
            table_function["countries"]()
        elif table == "general":
            table_function["general"]()
        elif table == "econ":
            table_function["econ"]()
        elif table == "social":
            table_function["social"]()
        elif table == "environment":
            table_function["environment"]

    def create_countries_table(self):
        stmt = """
        CREATE TABLE Countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        link TEXT
        )
        """
        self.cursor.execute(stmt)
        self.conn.commit()

    def create_general_table(self):
        stmt = """
        CREATE TABLE GeneralInfo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id INTEGER,
        region TEXT,
        membership_date TEXT,
        population INTEGER,
        population_density REAL,
        surface_area INTEGER,
        sex_ratio REAL,
        capital_city TEXT,
        capital_population REAL,
        currency TEXT,
        exchange_rate REAL
        )
        """
        self.cursor.execute(stmt)
        self.conn.commit()

    def create_econ_table(self):
        stmt = """
        CREATE TABLE EconIndicator (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id INTEGER,
        year INTEGER,
        GDP INTEGER,
        "GDP growth" REAL,
        "GDP per capita" REAL,
        "Agriculture" REAL,
        "Industry" REAL,
        "Services" REAL,
        "Agriculture employment" REAL,
        "Industry employment" REAL,
        "Services employment" REAL,
        "Unemployment rate" REAL,
        "Labour participation (females)" REAL,
        "Labour participation (males)" REAL,
        "CPI" INTEGER,
        "Agricultural index" INTEGER,
        "Industrial index" INTEGER,
        "Exports" INTEGER,
        "Imports" INTEGER,
        "Trade balance" INTEGER,
        "Current account" INTEGER
        )
        """
        self.cursor.execute(stmt)
        self.conn.commit()

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

    def create_social_table(self):
        stmt = """
        CREATE TABLE SocialIndicator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            year INTEGER,
            "Population growth" REAL,
            "Urban population" REAL,
            "Urban population growth" REAL,
            "Fertility rate" REAL,
            "Life expectancy (females)" REAL,
            "Life expectancy (males)" REAL,
            "Population distribution (children)" REAL,
            "Population distribution (elders)" REAL,
            "Migrant" REAL,
            "Migrant ratio" REAL,
            "Refugees" REAL,
            "Infant mortality" REAL,
            "Health expenditure" REAL,
            "Physicians ratio" REAL,
            "Education expenditure" REAL,
            "Primary enroll ratio (females)" REAL,
            "Primary enroll ratio (males)" REAL,
            "Secondary enroll ratio (females)" REAL,
            "Secondary enroll ratio (males)" REAL,
            "Tertiary enroll ratio (females)" REAL,
            "Tertiary enroll ratio (males)" REAL,
            "Homicide rate" REAL,
            "Women in parliaments" REAL
        )
        """
        self.cursor.execute(stmt)
        self.conn.commit()

    def create_environment_table(self):
        stmt = """
        CREATE TABLE EnvIndicator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            year INTEGER,
            internet_individual REAL,
            threatened_species INTEGER,
            forested_area REAL,
            carbon_dioxide_emission REAL,
            carbon_dioxide_emission_per_capita REAL,
            energy_production INTEGER,
            energy_supply INTEGER,
            protected_sites_ratio REAL,
            drinking_water_urban REAL,
            drinking_water_rural REAL,
            sanitation_urban REAL,
            sanitation_rural REAL,
            assistance_received REAL
        )
        """
        self.cursor.execute(stmt)
        self.conn.commit()

    def drop_tables(self):
        # stmt = """
        # DROP TABLE IF EXISTS Countries;
        # DROP TABLE IF EXISTS GeneralInfo;
        # DROP TABLE IF EXISTS EconIndicator;
        # DROP TABLE IF EXISTS SocialIndicator;
        # DROP TABLE IF EXISTS EnvIndicator;
        # """
        stmt = """
        DROP TABLE IF EXISTS EconIndicator;
        """
        self.cursor.executescript(stmt)
        self.conn.commit()
