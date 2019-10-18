import re


def format_value(number):
    number = number.strip()
    number = number.replace("~", "")
    if number == "...":
        return None
    if re.search("(~)?\d+\.?\d+\s?/~?\s*~?\d+\.?\d+", number):
        first, second = number.split("/")
        return (float(first.strip()), float(second.strip()))
    if re.search("-?\s?\d+\.\d+$", number):
        number = number.replace(" ", "")
        return float(number)
    number = number.replace(" ", "")
    return int(number)


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
