#!/usr/bin/env python
# coding: utf-8

import re
import os

import pdfplumber
import pandas as pd
from collections import namedtuple

# prototype of line
Line = namedtuple('Line', 'name title function direct_email direct_phone')

# regex search patterns
contact_re = re.compile(r'[Ee]xecutives [Aa]t [Tt]his [Ll]ocation')
line_re = re.compile(r'([a-zA-Z]+\.?\s?[a-zA-Z ]+)\s{2}([a-zA-Z ]+)\s{2}([a-zA-Z]+,?\s?[a-zA-Z]+)\s{2}([a-zA-Z\.@ ]+)\s{2}([\d-]+)')

# Get file
file = "Enbridge-Reserve Pump Station Reserve, MT.pdf"

# initiate lines array
lines = []

# read PDF and grab line(s)
with pdfplumber.open(file) as pdf:
    pages = pdf.pages
    for page in pages:
        text = page.extract_text().split('\n')

# Read each line and search for against start of contact block

        for i, line in enumerate(text):
            start = contact_re.search(line)
            
            if start:
                contact = text[i+2]
            
# if contact block is found, search for contact and append to lines
                if line_re.search(contact):
                    items = contact.split("  ")
                    items[3] = items[3].replace(' ', '')
                    lines.append(Line(*items))

# transform lines to pandas dataframe, write to a CSV
df = pd.DataFrame(lines)
df.to_csv("Contact_List.csv", index=False)