#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
title:          fxaddon-report.py
description:    Fetch Firefox addon users, license, strings, rating and locales for a given list
usage:          python fetchlocales.py >> file.csv
license:        MPL 2.0
'''

import os, errno, requests, zipfile, sys, json
import config

addons = config.addons
apiURL = config.apiURL
tmp = config.tmp

try:
    os.mkdir(tmp)
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise
    pass

# Output headers
output = '"ID", "Name", "Users", "License", "Strings", "Rating", "Locales", "AMO description locales"\n'

def getInfo(url):
    # It will return id, link, title and users for a given addon url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    descriptionLocales = []

    addonURL = url.replace('https://addons.mozilla.org/firefox/','')
    apiJson = requests.get(apiURL+addonURL, headers=headers)
    addonData = apiJson.json()

    id = addonData['slug']
    link = addonData['current_version']['files'][0]['url']
    title = addonData['name']['en-US']
    users = addonData['average_daily_users']
    try:
        license = addonData['current_version']['license']['name']['en-US']
    except:
        license = "None"
    rating = addonData['ratings']['average']

    for key, value in addonData['description'].iteritems() :
        descriptionLocales.append(str(key))

    return {
        'link': link,
        'id': str(id),
        'title': title.encode('utf-8'),
        'users': str(users),
        'license': str(license),
        'rating': str(rating),
        'descriptionLocales': descriptionLocales
    }

for a in addons:
    # We store locales in a set to avoid duplicates as a result of reading folders
    locales = set()
    addonInfo = getInfo(a)
    link = addonInfo['link']
    strings = "0"

    # Downloading
    r = requests.get(link)
    with open(tmp + '/addon.xpi', 'wb') as f:
        f.write(r.content)

    # Listing xpi content and filtering _locales folder
    xpifile = zipfile.ZipFile(tmp + '/addon.xpi')

    # Cleaning up strings to remove _locales and backslashes
    for f in filter(lambda x:'_locales/' in x, xpifile.namelist()):
        f = f.replace('_locales/', '').replace('messages.json','')

        if f.endswith('/'):
            locales.add(f.replace('/', ''))

    locales = str(sorted(list(locales)))

    # Checking English strings
    if '_locales/en/messages.json' in xpifile.namelist():
        messagesFile = '_locales/en/messages.json'
    elif '_locales/en_US/messages.json' in xpifile.namelist():
        messagesFile = '_locales/en_US/messages.json'
    else:
        messagesFile = None

    if messagesFile:
        xpifile.extract(messagesFile, tmp)
        with open(tmp + '/' + messagesFile, 'r') as json_file:
            try:
                strings = str(len(json.load(json_file)))
            except ValueError, e:
                strings = "Error"
    else:
        strings = "0"

    output += '"' + addonInfo['id'] + '","' + addonInfo['title'] + '","' + addonInfo['users'] + '","' + addonInfo['license'] + '"' + ',"' + strings + '","' + addonInfo['rating'] + '","' + locales + '","' + str(addonInfo['descriptionLocales']) + '"\n'

print output
