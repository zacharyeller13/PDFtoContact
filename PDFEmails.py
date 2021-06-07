#!/usr/bin/env python
# coding: utf-8

import re
import os

import pdfplumber
import pandas as pd
from collections import namedtuple

Line = namedtuple('Line', 'name title function direct_email direct_phone')

contact_re = re.compile(r'[Ee]xecutives [Aa]t [Tt]his [Ll]ocation')
line_re = re.compile(r'([a-zA-Z]+\.?\s?[a-zA-Z ]+)\s{2}([a-zA-Z ]+)\s{2}([a-zA-Z]+,?\s?[a-zA-Z]+)\s{2}([a-zA-Z\.@ ]+)\s{2}([\d-]+)')

file = "Enbridge-Reserve Pump Station Reserve, MT.pdf"

lines = []

with pdfplumber.open(file) as pdf:
    pages = pdf.pages
    for page in pages:
        text = page.extract_text().split('\n')
        
        for i, line in enumerate(text):
            start = contact_re.search(line)
            
            if start:
                contact = text[i+2]
            
                if line_re.search(contact):
                    items = contact.split("  ")
                    items[3] = items[3].replace(' ', '')
                    lines.append(Line(*items))
        
            if line_re.search(line):
                print(line)

df = pd.DataFrame(lines)
print(df.head())