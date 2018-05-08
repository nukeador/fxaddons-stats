#!/usr/bin/python
# -*- coding: utf-8 -*-

### This file defines some configuration variables for the rest of the scripts

# List here all the urls for the addons you want to fetch
addons = [
    'https://addons.mozilla.org/firefox/addon/easyscreenshot/',
    'https://addons.mozilla.org/firefox/addon/flash-video-downloader/',
]

# Locales names to fetch from stats json
# Exact names can we seen in https://addons.mozilla.org/firefox/addon/easyscreenshot/statistics/usage/languages/
locales = [
    u'English (US) (en-us)',
    u'Deutsch (de)',
    u'Français (fr)',
    u'Español (de España) (es-es)',
    u'Português (do Brasil) (pt-br)',
    u'Русский (ru)',
    u'中文 (简体) (zh-cn)',
    u'Polski (pl)',
    u'Italiano (it)',
    u'Español (de México) (es-mx)',
    u'日本語 (ja)',
    u'Nederlands (nl)'
]

apiURL = 'https://services.addons.mozilla.org/api/v3/addons/'

# Subfolder to store the string files
folder = 'files'
# Folder for temporal downloads
tmp = 'tmp'
