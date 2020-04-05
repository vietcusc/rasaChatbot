import json
import requests
import feedparser
import urllib.request
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

xl = pd.ExcelFile('diachi.xlsx')
df = pd.read_excel(xl, 0, header=None)
d={}
print(df.iloc[1,:])
'''
for i in range(1,len(df.iloc[:, 0])):
    dulieu = df.iloc[i,:]
    d[str(dulieu[3])]  =  str(dulieu[4])

with open ('diachi.json','w') as f:
    json.dump(d,f)
'''
with open('donvi.json') as file_write:
    d1 = json.load(file_write)

print(d1)

