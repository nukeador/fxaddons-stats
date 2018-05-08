## Firefox Addons scripts

These are a set of script to generate some reports about specific addons.

### config.py

Configure here the list of `addons` urls and `locales` you want to get reports from.

### fxaddon-report.py

Fetch Firefox addon users, license, strings, rating and locales for a given list

``python fetchlocales.py >> report.csv``

### fxaddon-users.py

Returns number of users per locale

``python fxaddon-users.py >> report-users.csv``

### fxaddon-getstrings.py

Downloads Firefox addon English strings from both the extension and Mozilla Addons site description

``python fxaddon-getstrings.py``

Strings are stored in the `files` subfolder with the id of the addon as folder.
