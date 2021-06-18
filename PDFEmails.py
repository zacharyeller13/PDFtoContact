#!/usr/bin/env python
# coding: utf-8

import re
import glob

import os
from shutil import move

import pdfplumber
import pandas as pd
from collections import namedtuple

# define helper functions: indexing function, email address check, get_company
def index_in_list(list_, index):
    return index < len(list_)

def email_check(list_, index):
    return '@' in list_[index]

def get_company(pages):
    page = pages[0]

    line = page.extract_text().split('\n')[1]
    company = line.split("Company ID:")[0].strip()

    return company

def get_city_state(pages, pattern):
    page = pages[0]
    lines = page.extract_text().split('\n')

    for line in lines:
        city_state = pattern.search(line)
        if city_state:
            city_state = [city_state[1].strip(), city_state[2].replace(" ",""), city_state[3].replace(" ", "")]
            return city_state
    return

# prototype of line
Line = namedtuple('Line', 'name title function direct_email direct_phone site city state zip')

# regex search patterns
line_re = re.compile(r"([a-zA-Z-\.() ]+)\s{2}([a-zA-Z\s\.\-,&]+)\s{2}([a-zA-Z,/&\s]+)\s{2}([a-zA-Z\._]*@ ?[a-zA-Z\.]*)*\s*([Ext: \d-]*)")
city_re = re.compile(r"^([a-zA-Z\s]+),?\s+([A-Z]+ *[A-Z]+)\s+([\d\s]+)")

# Get all files in folder
files = glob.glob('*.pdf')

# initiate lines array
lines = []

# for each PDF in files read PDF and grab line(s)
for file in files:

    print("Processing file {}".format(file))

    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        
        try:
            site = get_company(pages)                       # Get the site location
            city_state_zip = get_city_state(pages, city_re) # Get city, state, zip of location

            for page in pages:
                text = page.extract_text().split('\n')
                
# Read each line and search for against line_re pattern, appending to lines if found
                for line in text:

                    if line_re.search(line) and not any(x in line for x in ["Name", "LLC", "Co."]): # eliminate title block & false matches          
                        items = line_re.search(line)[0].split("  ")                                 # split on space*2
                        items[3] = items[3].replace(' ', '')                                        # replace space in email address
                        contact = [item.strip() for item in items if item.strip()]                  # if contact block is found, split between items and append to lines

                        if not index_in_list(contact, 4):                                           # if phone number OR email address is missing, add None at that index
                            if not email_check(contact, 3):
                                contact.insert(3, None)
 
                            else:
                                contact.append(None)

                        lines.append(Line(*contact, site, *city_state_zip))
        except TypeError:
            os.makedirs("errors", exist_ok=True)
            move(file, "./errors/")

        except IndexError:
            os.makedirs("errors", exist_ok=True)
            move(file, "./errors/")
            input("IndexError")         

# transform lines to pandas dataframe, write to a CSV
df = pd.DataFrame(lines)
df.drop_duplicates(inplace=True)
df.to_csv("Contact_List.csv", index=False)
print("Done")