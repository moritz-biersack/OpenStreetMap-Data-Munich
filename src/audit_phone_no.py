# -*- coding: utf-8 -*-
"""Take phone numbers, check their format and return harmonized form.
"""

import sys
import re

PHONE_FILE = 'phone-nodes.txt'

def read_phone_no(phone_file=PHONE_FILE):
    """Read phone numbers from file and return list of phone numbers.

    Args:
        phone_file (str): file name including phone numbers (one per line)

    Returns:
        list: phone numbers
    """
    phone_numbers = []

    with open(phone_file, 'r') as f:
        for line in f:
            # split at ','/';', in case there are several numbers in line
            numbers = re.split(r'[,;]', line)
            # strip every number and add to `phone_numbers`
            for num in numbers:
                phone_numbers.append(num.strip())

    return phone_numbers

def get_local_phone_no(raw_phone_no):
    """Find and return valid local phone number elements as list.
    Return empty list, if not valid.
    """
    return re.findall(r'^\(?\+?(00)?(49)?[ 0\-().]*89[ .\-/)]*([)/0-9\-. ]+$)',
                      raw_phone_no)

def get_mobile_phone_no(raw_phone_no):
    """Find and return valid mobile phone number elements as list.
    Return empty list, if not valid.
    """
    return re.findall(
        r'^\(?\+?(00)?(49)?[ 0\-().]*(1[567]\d)[ .\-/)]*([)/0-9\-. ]+$)',
        raw_phone_no)


def harmonized_local_phone_no(local_phone_no_match):
    """Harmonize and return a local phone number.
    For example '+49 89 1234567'.
    """
    actual_phone_no = local_phone_no_match[0][-1]
    clean_phone_no = ' '.join(
        ['+49 89', re.sub(r'[^\d]', '', actual_phone_no)]
        )
    return clean_phone_no

def harmonized_mobile_phone_no(mobile_phone_no_match):
    """Harmonize and return a mobile phone number.
    For example '+49 171 12345678'.
    """
    actual_phone_no = mobile_phone_no_match[0][-1]
    clean_phone_no = ' '.join(
        ['+49', mobile_phone_no_match[0][-2], re.sub(r'[^\d]', '',
         actual_phone_no)]
        )
    return clean_phone_no

def get_clean_phone_no(raw_phone_no):
    """Check `raw_phone_no` and if it is valid, return harmonized number.

       Example return values:
       - '+49 89 12345678' (local number)
       - '+49 151 12345678' (mobile number).

       Returns None, if number is not valid.

    Args:
        raw_phone_no (str): raw phone number string.
    Returns:
        str: Harmonized phone number
    """
    local_phone_no_match = get_local_phone_no(raw_phone_no)
    mobile_phone_no_match = get_mobile_phone_no(raw_phone_no)

    if len(local_phone_no_match) > 0:
        return harmonized_local_phone_no(local_phone_no_match)

    elif len(mobile_phone_no_match) > 0:
        return harmonized_mobile_phone_no(mobile_phone_no_match)

    else:
        # sys.stderr.write('Invalid phone#: ' + raw_phone_no + '\n')
        return None

def audit(phone_file=PHONE_FILE):
    """Start the phone number audit."""
    
    for phone_no in read_phone_no(phone_file):
        clean_phone_no = get_clean_phone_no(phone_no)
        if clean_phone_no is not None:
            l = len(phone_no)
            print phone_no + ' '*(24-l) + '-->\t' + clean_phone_no

if __name__ == '__main__':
    if len(sys.argv) is 2:
        audit(sys.argv[1])
    elif len(sys.argv) is 1:
        audit()
    else:
        sys.stderr.write('Pleas specify file name or leave blank')

