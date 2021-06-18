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
    try:
        return (x in list_[index] for x in ['@', "View Email", "ViewEmail"])
    except (IndexError, TypeError):
        return

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

# pull actual searching into a function to allow exiting function when reaching end of contact block
def search_lines(pages, pattern):
    contacts = []
    for page in pages:
        text = page.extract_text().split('\n')
    
        for line in text:

            if any(x in line for x in ["Corporate Family", "Parent Company", "My Notes", "Potential Competitors"]):
                return contacts

            elif pattern.search(line) and not any(x in line for x in ["Name", "Title", "Function"]):
                items = pattern.search(line)[0].split("  ")
                items[3] = items[3].replace(' ', '')
                contact = [item.strip() for item in items if item.strip()]
                
                while not index_in_list(contact, 4):
                    if not email_check(contact, 3):
                        contact.insert(3, None)

                    else:
                        contact.append(None)
            
                contacts.append(contact)
                
            else:
                continue

        return contacts

# prototype of line
Line = namedtuple('Line', 'name title function direct_email direct_phone site city state zip')

# regex search patterns
line_re = re.compile(r"([a-zA-Z-\.()' ]+)\s{2}([a-zA-Z\s\.\-,&]+)\s{2}([a-zA-Z,/&\s]+)\s{2}([a-zA-Z\._]+@ ?[\da-zA-Z\.\-]*)*\s*([Ext: \d-]*)")
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

# wrap in a try/except to catch TypeErrors and IndexErrors        
        try:
            site = get_company(pages)                       # Get the site location
            city_state_zip = get_city_state(pages, city_re) # Get city, state, zip of location
                         
# Read each line and search for against line_re pattern, appending to lines if found
            contacts = search_lines(pages, line_re)

            for contact in contacts:
                lines.append(Line(*contact, site, *city_state_zip))

        except TypeError:
            os.makedirs("errors/TypeError", exist_ok=True)
            move(file, "./errors/TypeError")

        except IndexError:
            os.makedirs("errors/IndexError", exist_ok=True)
            move(file, "./errors/IndexError")        

# transform lines to pandas dataframe, write to a CSV
df = pd.DataFrame(lines)
df.drop_duplicates(inplace=True)
df.to_csv("Contact_List.csv", index=False)
print("Done")