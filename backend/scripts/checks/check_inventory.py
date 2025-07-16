import sqlite3

conn = sqlite3.connect('prevostgo.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM coaches WHERE status = "available"')
count = cursor.fetchone()[0]
print(f'Total available coaches: {count}')

cursor.execute('SELECT converter, COUNT(*) as cnt FROM coaches WHERE status = "available" GROUP BY converter ORDER BY cnt DESC LIMIT 10')
print('\nTop converters:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()