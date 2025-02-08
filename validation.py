# Description: This file contains functions to validate the input data.

from datetime import datetime

def validate_fin(fin):
    if len(fin) != 9:
        print(f"FIN length is incorrect: {len(fin)}")
        return False
    if not fin[0].isalpha():
        print(f"First character is not a letter: {fin[0]}")
        return False
    if not fin[1:8].isdigit():
        print(f"Characters 2-8 are not digits: {fin[1:8]}")
        return False
    if not fin[-1].isalnum():
        print(f"Last character is not alphanumeric: {fin[-1]}")
        return False
    return True

def validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    