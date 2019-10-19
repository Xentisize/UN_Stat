import re


def format_value(value):
    print(value)
    if not value:
        return None

    value = value.strip()
    value = value.replace("~", "")
    if value == "...":
        return None
    if value == "... / ...":
        return value.split(" / ")
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


def clean_social_indicator_header(value):
    if value.startswith("Population growth"):
        return "Population growth"
    elif value.startswith("Urban population(% of"):
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

