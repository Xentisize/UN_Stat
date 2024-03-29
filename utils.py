import re
import pprint

p = pprint.PrettyPrinter(indent=4)


def format_value(value):
    p.pprint(value)
    if not value:
        return None

    value = value.strip()
    value = value.replace("~", "")
    if value == "...":
        return None
    if value == "... / ...":
        return (None, None)
    if re.search("^\.{3}\s*/\s*\d+", value):
        first, second = value.split("/")
        # print(f"First value: {first}")
        # print(f"Second value: {second}")
        first = first.strip()
        second = second.strip()
        return (None, float(second))
    if re.search("^\d[\d\.]+ / \.{3}$", value):
        first, second = value.split("/")
        return (float(first.strip()), None)
    if re.search("^\.{3} / \d[\d\.]+$", value):
        first, second = value.split()
        return (None, float(second.strip()))
    if re.search("(~)?\d+\.?\d+\s?/~?\s*~?\d+\.?\d+", value):
        # split and format the fraction (dd / dd)
        first, second = value.split("/")
        first = first.replace(" ", "")
        second = second.replace(" ", "")
        return (float(first.strip()), float(second.strip()))
    if re.search("-?\s?\d+\.\d+$", value):
        # format decimal number
        value = value.replace(" ", "")
        return float(value)
    if re.search("^\d+\s?\d*$", value):
        # format integer with space separators
        value = value.replace(" ", "")
        return int(value)
    if re.search("\([a-zA-Z]+\)?$", value):
        # format the currency Name (Abbreviation)
        return value
    if re.search("[a-zA-Z\s]+", value):
        # format the string
        return value
    if re.search("\d+-[a-zA-Z]+-\d+", value):
        return value
    value = value.replace(" ", "")
    return int(value)


def remove_trailing_chars(value):
    m = re.search("\d+\s?\.?\d?([a-z,]+)", value) or re.search(
        "[\.]{3}([a-zA-Z,]+)$", value
    )
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


def clean_general_information_header(value):
    if value.startswith("Region"):
        return "Region"
    elif value.startswith("UN membership"):
        return "UN membership date"
    elif value.startswith("Population"):
        return "Population"
    elif value.startswith("Pop. density"):
        return "Population density"
    elif value.startswith("Surface area"):
        return "Surface area"
    elif value.startswith("Sex ratio"):
        return "Sex ratio"
    elif re.search("Capital city$", value):
        return "Capital city"
    elif value.startswith("Capital city pop."):
        return "Capital population"
    elif value.startswith("National currency"):
        return "National currency"
    elif value.startswith("Exchange rate"):
        return "Exchange rate"


def clean_social_indicator_header(value):
    if value.startswith("Population growth"):
        return "Population growth"
    elif re.search("^Urban population[a-zA-Z,]*\s?\(", value):
        print("Urban reached")
        return "Urban population"
    elif value.startswith("Urban population growth"):
        return "Urban population growth"
    elif value.startswith("Fertility"):
        return "Fertility rate"
    elif value.startswith("Life expectancy"):
        # Life expectancy for males is pending
        return "Life expectancy (females)"
    elif value.startswith("Population age"):
        # Population distribution for elders is pending
        return "Population distribution (children)"
    elif value.startswith("International migrant"):
        # Migrant ratio is pending
        return "Migrant"
    elif value.startswith("Refugees"):
        return "Refugees"
    elif value.startswith("Infant"):
        return "Infant mortality"
    elif value.startswith("Health: Current"):
        return "Health expenditure"
    elif value.startswith("Health: Physicians"):
        return "Physicians ratio"
    elif value.startswith("Education: Government"):
        return "Education expenditure"
    elif value.startswith("Education: Primary"):
        # male is pending
        return "Primary enroll ratio (females)"
    elif value.startswith("Education: Secondary"):
        # male is pending
        return "Secondary enroll ratio (females)"
    elif value.startswith("Education: Tertiary"):
        # male is pending
        return "Tertiary enroll ratio (females)"
    elif value.startswith("Intentional homicide"):
        return "Homicide rate"
    elif value.startswith("Seats"):
        return "Women in parliaments"


def clean_econ_indicator_header(value):
    # shorthand to save typing
    v = value
    if v.startswith("GDP:"):
        return "GDP"
    elif v.startswith("GDP growth"):
        return "GDP growth"
    elif v.startswith("GDP per"):
        return "GDP per capita"
    elif v.startswith("Economy: Agriculture"):
        return "Agriculture"
    elif v.startswith("Economy: Industry"):
        return "Industry"
    elif v.startswith("Economy: Services"):
        return "Services"
    elif v.startswith("Employment in agriculture"):
        return "Agriculture employment"
    elif v.startswith("Employment in industry"):
        return "Industry employment"
    elif v.startswith("Employment in services"):
        return "Services employment"
    elif v.startswith("Unemployment"):
        return "Unemployment rate"
    elif v.startswith("Labour"):
        return "Labour participation (females)"
    elif v.startswith("CPI"):
        return "CPI"
    elif v.startswith("Agricultural"):
        return "Agricultural index"
    elif v.startswith("Index of industrial"):
        return "Industrial index"
    elif v.startswith("International trade: exports"):
        return "Exports"
    elif v.startswith("International trade: imports"):
        return "Imports"
    elif v.startswith("International trade: balance"):
        return "Trade balance"
    elif v.startswith("Balance of payments"):
        return "Current account"


def clean_env_indicator_header(value):
    # shorthand for saving typing
    v = value
    if v.startswith("Individuals using the Internet"):
        return "Internet usage"
    elif v.startswith("Research"):
        return "Research expenditure"
    elif v.startswith("Threatened"):
        return "Threatened species"
    elif v.startswith("Forested"):
        return "Forested area"
    elif v.startswith("CO2"):
        # CO2 per capita pending
        return "CO2 emission"
    elif v.startswith("Energy production"):
        return "Energy production"
    elif v.startswith("Energy supply"):
        return "Energy supply"
    elif v.startswith("Tourist"):
        return "Tourists"
    elif v.startswith("Important sites"):
        return "Important sites"
    elif v.startswith("Pop. using improved drinking"):
        # rural is pending
        return "Drinking water (urban)"
    elif v.startswith("Pop. using improved sanitation"):
        # rural is pending
        return "Sanitation (urban)"
    elif v.startswith("Net Official Development Assist. disbursed"):
        return "Assist disbursed"
    elif v.startswith("Net Official Development Assist. received"):
        return "Assist received"
