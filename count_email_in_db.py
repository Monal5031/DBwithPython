import sqlite3

connection = sqlite3.connect('emaildb.sqlite')
cursor = connection.cursor()

cursor.execute('''
DROP TABLE IF EXISTS Counts''')

cursor.execute('''
CREATE TABLE Counts (email TEXT, count INTEGER)''')

file_name = input('Enter file name')
if (len(file_name) < 1): file_name = 'mbox-short.txt'

file_handle = open(file_name)
for line in file_handle:
	if not line.startswith('From: '): continue
	pieces = line.split()
	email = pieces[1]
	cursor.execute('SELECT count FROM Counts WHERE email = ?', (email,))
	row = cursor.fetchone()
	if row is None:
		cursor.execute('''INSERT INTO Counts (email, count)
			VALUES (?,1)''', (email,))
	else:
		cursor.execute('UPDATE Counts SET count = count + 1 WHERE email = ?', (email,))
	connection.commit()

sql_string = 'SELECT email, count FROM Counts ORDER BY count DESC LIMIT 10'

for row in cursor.execute(sql_string):
	print(str(row[0]), row[1])

cursor.close()
