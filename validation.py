import re

def is_valid_username(input_str):
    pattern = r"^(?!.*\s)[A-Za-z0-9_.-]{6,}$"
    return bool(re.match(pattern, input_str))

def is_valid_password(input_str):
    # Check if the input matches the pattern
    pattern = r"^(?=.*[0-9])(?=.*[\W_])(?!.*\s)[A-Za-z0-9\W_]{6,}$"
    return bool(re.match(pattern, input_str))
