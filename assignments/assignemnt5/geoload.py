import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys


api_key =  'AIzaSyBhPTohBXcCrNSH5SFDg2YjcyT16laK7yA'
# If you have a Google Places API key, enter it here
# api_key = 'AIzaSy...IDByT70'

if not api_key:
    service_url = 'http://py4e-data.dr-chuck.net/geojson?'
else:
    service_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'

# Additional detail for urllib
# http.client.HTTPConnection.debuglevel = 1

connection = sqlite3.connect('geodata.sqlite')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

# Ignore SSL certificates
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

file_handle = open('where.data')
count = 0
for line in file_handle:
    if count > 200:
        print('Retrieved 200 Locations, restart to retrieve more')
        break
    address = line.strip()
    print()
    cursor.execute('SELECT geodata FROM Locations WHERE address = ?',
        (memoryview(address.encode()),))

    try:
        data = cursor.fetchone()[0]
        print('Found in database', address)
        continue
    except:
        pass
    parameters = dict()
    parameters["query"] = address
    if api_key is not False: parameters['key'] = api_key
    url = service_url + urllib.parse.urlencode(parameters)

    print('Retrieving', url)
    url_handle = urllib.request.urlopen(url, context=context)
    data = url_handle.read().decode()
    print('Retrieved', len(data), 'characters', data[:20].replace('\n',' '))
    count += 1

    try:
        js = json.loads(data)
    except:
        print(data)
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS'):
        print('====Failure to Retrieve=====')
        print(data)
        break

    cursor.execute('''INSERT INTO Locations (address, geodata)
        VALUES ( ? , ? )''', (memoryview(address.encode()), memoryview(data.encode())))
    connection.commit()
    if count % 10 == 0:
        print('Pausing for a bit....')
        time.sleep(5)


print('Run geodump.py to read data from the database so you can visualize')