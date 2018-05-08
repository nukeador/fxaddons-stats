#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
title:          fxaddon-users.py
description:    Returns number of users per locale
usage:          python fxaddon-users.py >> file.csv
license:        MPL 2.0
'''

import requests, json
import config
from datetime import datetime, timedelta

addons = config.addons
locales = config.locales

endDate = datetime.today().strftime('%Y%m%d')
startDate =  datetime.today() - timedelta(days=30)
startDate = startDate.strftime('%Y%m%d')

# File headers
output = '"Addon", "Total",'
for l in locales:
    output += '"' +l.encode('utf8') + '",'
output += '\n'

for a in addons:
    id = a.replace('https://addons.mozilla.org/firefox/addon/','').replace('/','')
    output += '"' + id + '",'

    jsonURL = a + 'statistics/locales-day-' + startDate + '-' + endDate + '.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0'}

    jsonData = requests.get(jsonURL, headers=headers)

    try:
        jsonData = jsonData.json()
    except:
        jsonData = None

    if jsonData:
        output += '"' + str(jsonData[0]['count']) + '",'
        for l in locales:
            try:
                users = str(jsonData[0]['data'][l])
                output += '"' + users + '",'
            except:
                output += '"Error",'
    output += '\n'

print output.decode('utf8')
