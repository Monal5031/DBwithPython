import xml.etree.ElementTree as ET
import sqlite3
import urllib.request, urllib.parse, urllib.error
import ssl


connection = sqlite3.connect('trackdb.sqlite')
cursor = connection.cursor()

# Data url
url = 'http://www.py4inf.com/code/tracks/Library.xml'


# Ignore SSL certificate errors
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE



def fetch_data():
	# Headers needed to prove that no bot is working.
	request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	url_handle = urllib.request.urlopen(request, context=context)
	# Data we read is not unicode so we need to decode
	data = url_handle.read().decode()
	return data


# <key> Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist></key><string>Queen</string>
def lookup(d, key):
	found = False
	for child in d:
		if found: return child.text
		if child.tag == 'key' and child.text == key:
			found = True
	return None



# Make some fresh tables using executescript()
cursor.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	name TEXT UNIQUE
);

CREATE TABLE ALBUM (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	artist_id INTEGER,
	title TEXT UNIQUE
);

CREATE TABLE Track (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	title TEXT UNIQUE,
	album_id INTEGER,
	len INTEGER, rating INTEGER, count INTEGER
);
''')


data = fetch_data()
data = ET.fromstring(data)
all = data.findall('dict/dict/dict')
print('Dict count:', len(all))
for entry in all:
	'''
	for d in entry:
		print(d.tag,':',d.text)
	print('\n\n\n\n\n\n\n\n')
	'''
	if lookup(entry, 'Track ID') is None:
		#print('track')
		continue
	name = lookup(entry, 'Name')
	artist = lookup(entry, 'Artist')
	album = lookup(entry, 'Album')
	count = lookup(entry, 'Play Count')
	rating = lookup(entry, 'Rating')
	length = lookup(entry, 'Total Time')

	if name is None or artist is None or album is None:
		continue

	print(name, artist, album, count, rating, length)

	cursor.execute('''INSERT OR IGNORE INTO Artist (name)
		VALUES ( ? )''', ( artist, ))
	cursor.execute('SELECT id FROM Artist WHERE name = ?', ( artist, ))
	artist_id = cursor.fetchone()[0]

	cursor.execute('''INSERT OR IGNORE INTO Album (title, artist_id)
		VALUES ( ?, ?)''', (album, artist_id) )
	cursor.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
	album_id = cursor.fetchone()[0]

	cursor.execute('''INSERT OR REPLACE INTO Track
		(title, album_id, len, rating, count)
		VALUES ( ?, ?, ?, ?, ?)''',
		( name, album_id, length, rating, count) )

connection.commit()
cursor.close()
