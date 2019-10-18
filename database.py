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
        industrial_index INTEGER,
        exports INTEGER,
        imports INTEGER,
        trade_balance INTEGER,
        current_account INTEGER
        )
        """
        self.cursor.execute(stmt)
        self.conn.commit()

    def create_social_table(self):
        stmt = """
        CREATE TABLE SocialIndicator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            year INTEGER,
            population_growth REAL,
            urban_population REAL,
            urban_population_growth REAL,
            fertility_rate REAL,
            life_expectancy_females REAL,
            life_expectancy_males REAL,
            population_distribution_children REAL,
            population_distribution_adults REAL,
            migrant REAL,
            migrant_ratio REAL,
            refugees REAL,
            infant_mortality REAL,
            health_expenditure REAL,
            physicians_ratio REAL,
            education_expenditure REAL,
            primary_enroll_ratio_females REAL,
            primary_enroll_ratio_males REAL,
            secondary_enroll_ratio_females REAL,
            secondary_enroll_ratio_males REAL,
            tertiary_enroll_ratio_females REAL,
            tertiary_enroll_ratio_males REAL,
            homicide_rate REAL,
            women_in_parliaments REAL
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
        stmt = """
        DROP TABLE IF EXISTS Countries;
        DROP TABLE IF EXISTS GeneralInfo;                
        DROP TABLE IF EXISTS EconIndicator;
        DROP TABLE IF EXISTS SocialIndicator;
        DROP TABLE IF EXISTS EnvIndicator;
        """
        self.cursor.executescript(stmt)
        self.conn.commit()
