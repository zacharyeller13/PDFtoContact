#!/usr/bin/env python
# coding: utf-8

import re
import glob

import pdfplumber
import pandas as pd
from collections import namedtuple

# prototype of line
Line = namedtuple('Line', 'name title function direct_email direct_phone')

# regex search patterns
contact_re = re.compile(r'[Ee]xecutives [Aa]t [Tt]his [Ll]ocation')
line_re = re.compile(r'([a-zA-Z]+\.?\s?[a-zA-Z ]+)\s{2}([a-zA-Z ]+)\s{2}([a-zA-Z]+,?\s?[a-zA-Z]+)\s{2}([a-zA-Z\.@ ]+)\s{2}([\d-]+)')

# Get all files in folder
files = glob.glob('*.pdf')

# initiate lines array
lines = []

# for each PDF in files read PDF and grab line(s)
for file in files:

    print("Processing file {}".format(file))

    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        for page in pages:
            text = page.extract_text().split('\n')

# Read each line and search for against line_re pattern
            for line in text:
                if line_re.search(line):                

# if contact block is found, split between items and append to lines
                    items = line.split("  ")
                    items[3] = items[3].replace(' ', '')
                    lines.append(Line(*items))

# transform lines to pandas dataframe, write to a CSV
df = pd.DataFrame(lines)
df.to_csv("Contact_List.csv", index=False)
print("Done")