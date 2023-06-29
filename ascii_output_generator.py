def find_prefix(string, prefixes):
    return next((prefix for prefix in prefixes if string.lower().startswith(prefix.lower() + ':')), None)


def longest_value_length(field_name):
    return max(map(len, field_name))


def generate_ascii_table_from_string(input_str, config, logger=None):
    # Split input string by newline characters to get each row
    lines = input_str.strip().split('\n')
    possible_fields = config.keys()
    max_field_name_len = longest_value_length(possible_fields) + 1

    result = dict()
    last_name = ''

    # Create the header row for the ASCII table
    header = f"{'Field Name':<{max_field_name_len}}| {'Field Value':<}"

    # Create the separator row for the ASCII table
    separator = '+' + '-' * (max_field_name_len - 1) + '|' + '-' * 50 + '+'

    # Initialize the ASCII table with the header and separator rows
    table = [header, separator]

    # Loop through the lines in the input string
    for line in lines:
        try:
            # Split the line into the field name and field value
            name, value = line.split(':', maxsplit=1)
            table.append(f"{name.strip():<{max_field_name_len}}| {value.strip():<}")
            result[name] = value.strip()
            last_name = name
        except ValueError:
            # Handle the case where there is no ':' in the line
            if last_name != '':
                table[-1] += line.strip()
                result[last_name] += line.strip()
            else:
                continue
        # Add the field name and field value to the table
    # Add the final separator row to the table
    table.append(separator)

    # Join the rows of the table into a single string
    table_str = '\n'.join(table)

    return table_str, result


def generate_ascii_table_from_json(input_json, config, logger):
    # Split input string by newline characters to get each row
    # lines = input_json.strip().split('\n')
    possible_fields = config.keys()
    max_field_name_len = longest_value_length(possible_fields) + 1

    # Create the header row for the ASCII table
    header = f"{'Field Name':<{max_field_name_len}}| {'Field Value':<}"

    # Create the separator row for the ASCII table
    separator = '+' + '-' * (max_field_name_len - 1) + '|' + '-' * 50 + '+'

    # Initialize the ASCII table with the header and separator rows
    table = [header, separator]

    # Loop through the lines in the input string
    for name, value in input_json.items():
        if name is not None:
            if value is None:
                value = ""
            table.append(f"{name.strip():<{max_field_name_len}}| {value.strip():<}")
    # Add the final separator row to the table
    table.append(separator)

    # Join the rows of the table into a single string
    table_str = '\n'.join(table)

    return table_str
