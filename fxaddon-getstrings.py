#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
title:          fxaddon-getstrings.py
description:    Downloads Firefox addon strings from both the extension and
                Mozilla Addons site description
usage:          python fxaddon-getstrings.py
license:        MPL 2.0
'''

import os, errno, requests, zipfile, json, shutil
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
    addonData = json.loads(apiJson.text)

    id = addonData['slug']
    link = addonData['current_version']['files'][0]['url']
    title = addonData['name']
    description = addonData['description']
    summary = addonData['summary']

    return {
        'link': link,
        'id': str(id),
        'title': title,
        'description': description,
        'summary': summary,
    }

def listInfoStore(locale, addonInfo, folder):
    # Storing the English strings from AMO
    # If not found, we'll use empty
    try:
        title = addonInfo['title'][locale]
    except KeyError, e:
        title = ""
    try:
        description = addonInfo['description'][locale]
    except KeyError, e:
        description = ""
    try:
        summary = addonInfo['summary'][locale]
    except KeyError, e:
        summary = ""

    listingInfo = {
        'name': {
            'message': title
        },
        'description': {
            'message': description
        },
        'summary': {
            'message': summary
        }
    }

    listingInfo = json.dumps(listingInfo, indent=4, ensure_ascii=False).encode('utf8')

    # Let's make sure destination folder exists
    try:
        os.mkdir(folder)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        pass

    with open(folder + '/amo-listing.json', 'wb') as f:
        f.write(listingInfo)

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

    # Identify English strings location
    if '_locales/en/messages.json' in xpifile.namelist():
        messagesFile = '_locales/en/messages.json'
    elif '_locales/en_US/messages.json' in xpifile.namelist():
        messagesFile = '_locales/en_US/messages.json'
    else:
        messagesFile = None
        print 'Error: No English strings found for ' + addonInfo['title']['en-US']

    # We will extract all locales and move English strings to the parent folder
    if messagesFile:
        for file in xpifile.namelist():
            if file.startswith('_locales'):
                xpifile.extract(file, destinationFolder)

        os.rename(destinationFolder + '/' + messagesFile, destinationFolder + '/messages.json')

    # Sotring AMO listing information
    listInfoStore('en-US', addonInfo, destinationFolder)

    # Storing existing localizations from AMO listing
    # For each locale we create a json in the folder
    for key, value in addonInfo['description'].iteritems():
        if key != 'en-US':
            # Making sure _locales folder exists
            try:
                os.mkdir(destinationFolder + '/_locales')
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                pass
            listInfoStore(key, addonInfo, destinationFolder + '/_locales/' + key.replace('-','_'))

    # Cleaning any remaining 'en' or 'en_US' folders
    shutil.rmtree(destinationFolder + '/_locales/' + 'en/', ignore_errors=True)
    shutil.rmtree(destinationFolder + '/_locales/' + 'en_US/', ignore_errors=True)
