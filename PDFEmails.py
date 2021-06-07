#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re

import pdfplumber
import pandas as pd
from collections import namedtuple


# In[15]:


Line = namedtuple('Line', 'name title function direct_email direct_phone')


# In[16]:


contact_re = re.compile(r'[Ee]xecutives [Aa]t [Tt]his [Ll]ocation')
line_re = re.compile(r'([a-zA-Z]+\.?\s?[a-zA-Z ]+)\s{2}([a-zA-Z ]+)\s{2}([a-zA-Z]+,?\s?[a-zA-Z]+)\s{2}([a-zA-Z\.@ ]+)\s{2}([\d-]+)')


# In[20]:


file = "Enbridge-Reserve Pump Station Reserve, MT.pdf"


# In[21]:


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


# In[22]:


df = pd.DataFrame(lines)
df.head()


# In[ ]:




