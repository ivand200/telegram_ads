import psycopg2


conn = psycopg2.connect(
    database="ofwheuzn",
    user="ofwheuzn",
    password="QZ-umrXpxJxEin-C3nStyVimOrKCPcew",
    host="tiny.db.elephantsql.com",
)

cur = conn.cursor()


# sample = "%книга%"
# result = cur.execute("SELECT * FROM channels WHERE title ILIKE %(sample)s", {"sample": sample})
# raw = cur.fetchall()

