#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
title:          fxaddon-getstrings.py
description:    Downloads Firefox addon English strings from both the extension and
                Mozilla Addons site description
usage:          python fxaddon-getstrings.py
license:        MPL 2.0
'''

import os, errno, requests, zipfile, json
import config

# List here all the urls for the addons you want to fetch
addons = config.addons
apiURL = config.apiURL

# Subfolder to store the string files
folder = config.folder
# Folder for temporal downloads
tmp = config.tmp

try:
    os.mkdir(folder)
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise
    pass

try:
    os.mkdir(tmp)
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise
    pass

def getInfo(url):

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:59.0) Gecko/20100101 Firefox/59.0'}
    descriptionLocales = []

    addonURL = url.replace('https://addons.mozilla.org/firefox/','')
    apiJson = requests.get(apiURL+addonURL, headers=headers)
    addonData = apiJson.json()

    id = addonData['slug']
    link = addonData['current_version']['files'][0]['url']
    title = addonData['name']['en-US']
    description = addonData['description']['en-US']
    summary = addonData['summary']['en-US']

    return {
        'link': link,
        'id': str(id),
        'title': title.encode('utf-8'),
        'description': description,
        'summary': summary,
    }

for a in addons:
    # We store locales in a set to avoid duplicates as a result of reading folders

    addonInfo = getInfo(a)
    link = addonInfo['link']

    # Downloading
    r = requests.get(link)
    with open( tmp + '/addon.xpi', 'wb') as f:
        f.write(r.content)

    # Listing xpi content
    xpifile = zipfile.ZipFile(tmp + '/addon.xpi')

    # We will store each addon strings in a different folder
    destinationFolder = folder + '/' + addonInfo['id']
    try:
        os.mkdir(destinationFolder)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    # Extract English strings
    if '_locales/en/messages.json' in xpifile.namelist():
        messagesFile = '_locales/en/messages.json'
    elif '_locales/en_US/messages.json' in xpifile.namelist():
        messagesFile = '_locales/en_US/messages.json'
    else:
        messagesFile = None
        print 'Error: No English strings found'

    if messagesFile:
        xpifile.extract(messagesFile, destinationFolder)

    # Storing the strings from AMO
    listingInfo = {
        'name': {
            'message': addonInfo['title']
        },
        'description': {
            'message': addonInfo['description']
        },
        'summary': {
            'message': addonInfo['summary']
        }
    }
    listingInfo = json.dumps(listingInfo, indent=4, ensure_ascii=False).encode('utf8')

    with open(destinationFolder + '/amo-listing.json', 'wb') as f:
        f.write(listingInfo)
