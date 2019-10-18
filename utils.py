import re


def format_value(value):
    print(value)
    if not value:
        return None

    value = value.strip()
    value = value.replace("~", "")
    if value == "...":
        return None
    if re.search("(~)?\d+\.?\d+\s?/~?\s*~?\d+\.?\d+", value):
        # split and format the fraction (dd / dd)
        first, second = value.split("/")
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
    m = re.search("\d+\s?\.?\d?([a-z,]+)", value)
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


s = "Population growth ratef(average annual %)	Urban population(% of total population)	Urban population growth ratef(average annual %)	Fertility rate, totalf(live births per woman)	Life expectancy at birthf(females/males, years)	Population age distribution(0-14/60+ years old, %)	International migrant stock(000/% of total pop.)	Refugees and others of concern to UNHCR000	Infant mortality ratef(per 1 000 live births)	Health: Current expenditure(% of GDP)	Health: Physicians(per 1 000 pop.)	Education: Government expenditure(% of GDP)	Education: Primary gross enrol. ratio(f/m per 100 pop.)	Education: Secondary gross enrol. ratio(f/m per 100 pop.)	Education: Tertiary gross enrol. ratio(f/m per 100 pop.)	Intentional homicide rate(per 100 000 pop.)	Seats held by women in National Parliaments(%)"

headers = [
    "Population growth",
    "Urban population",
    "Urban population growth",
    "Fertility rate",
    "Life expectancy (females)",
    "Life expectancy (males)",
    "Population distribution (children)",
    "Population distribution (adults)",
    "Migrant",
    "Refugees",
    "Infant mortality",
    "Health expenditure ",
    "Physicians",
    "Education expenditure",
    "Primary enroll",
    "Secondary enroll",
]
