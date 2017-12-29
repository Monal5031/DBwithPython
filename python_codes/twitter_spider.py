import urllib.request, urllib.parse, urllib.error
import sqlite3
import sys
import ssl
import twurl
import json

TWITTER_URL = 'https://api.twitter.com/1.1/friends/list.json'

connection = sqlite3.connect('twitter_spider.sqlite')
cursor = connection.cursor()

cursor.execute('''
	CREATE TABLE IF NOT EXISTS Twitter
	(name TEXT, retrieved INTEGER, friends INTEGER)''')

# Ignore SSL certificate errors
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

while True:
	account = input('Enter a Twitter account, or quit')
	if len(account) < 1:
		cursor.execute('SELECT name FROM Twitter WHERE retrieved = 0 LIMIT 1')
		try:
			account = cursor.fetchone()[0]
		except:
			print('No unretrieved Twitter accounts found')
			continue
	url = twurl.augment(TWITTER_URL, {'screen_name': account, 'count': '5'})
	print('Retrieving', url)
	request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	url_handle = urllib.request.urlopen(request, context=context)
	# Data we read is not unicode so we need to decode
	data = url_handle.read().decode()
	headers = dict(url_handle.getheaders())

	print('Remaining', headers['x-rate-limit-remaining'])
	js = json.loads(data)
	# Checking
	# print(json.dumps(js, indent=4))

	cursor.execute('UPDATE Twitter SET retrieved=1 WHERE name = ?', (account, ))

	count_new = 0
	count_old = 0
	for u in js['users']:
		friend = u['screen_name']
		print(friend)
		cursor.execute('SELECT friends FROM Twitter WHERE name = ? LIMIT 1',
			           (friend, ))
		try:
			count = cursor.fetchone()[0]
			cursor.execute('UPDATE Twitter SET friends = ? WHERE name = ?',
				(count+1, friend))
			count_old += 1
		except:
			cursor.execute('''INSERT INTO Twitter (name, retrieved, friends)
				VALUES (?, 0, 1)''', (friend, ))
			count_new += 1
	print('New accounts=', count_new, '\nrevisited=', count_old)
	connection.commit()

cursor.close()
