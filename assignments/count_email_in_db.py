import urllib.request, urllib.parse, urllib.error
import sqlite3
import sys
import ssl


# DB connections
connection = sqlite3.connect('Assignment2.sqlite')
cursor = connection.cursor()

# Data url
url = 'https://www.py4e.com/code3/mbox.txt'


# Ignore SSL certificate errors
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def fetch_data():
	request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	url_handle = urllib.request.urlopen(request, context=context)
	# Data we read is not unicode so we need to decode
	data = url_handle.read().decode()
	return data

def run_db_queries():
	cursor.execute('''
	DROP TABLE IF EXISTS Counts''')

	cursor.execute('''
	CREATE TABLE Counts (org TEXT, count INTEGER)''')

	data = fetch_data()
	print('data has arrived')
	for line in data.split('\n'):
		print('.', end='', flush=True)
		if not line.startswith('From: '): continue
		pieces = line.split()
		org = pieces[1].split('@')[1]
		cursor.execute('SELECT count FROM Counts WHERE org = ?', (org,))
		row = cursor.fetchone()
		if row is None:
			cursor.execute('''INSERT INTO Counts (org, count)
				VALUES (?,1)''', (org,))
		else:
			cursor.execute('UPDATE Counts SET count = count + 1 WHERE org = ?', (org,))
	connection.commit()

	sql_string = 'SELECT org, count FROM Counts ORDER BY count DESC LIMIT 10'

	for row in cursor.execute(sql_string):
		print(str(row[0]), row[1])


run_db_queries()

cursor.close()
