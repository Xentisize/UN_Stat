import re


def format_value(value):
    if None:
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


headings = [
    "Region",
    "UN membership date",
    "Population",
    "Population density",
    "Surface area",
    "Sex ratio",
    "Capital city",
    "Capital population",
    "National currency" "Exchange rate",
]

{
    "Capital city": "Kabul",
    "Capital city pop.(000, 2018)": "4 011.8",
    "Exchange rate(per US$)": "69.5",
    "National currency": "Afghani (AFN)",
    "Pop. density(per km2, 2018)": "55.7",
    "Population(000, 2018)": "36 373",
    "Region": "Southern Asia",
    "Sex ratio(m per 100 f)": "106.2",
    "Surface area(km2)": "652 864",
    "UN membership date": "19-Nov-46",
}

