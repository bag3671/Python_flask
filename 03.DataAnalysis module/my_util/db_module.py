import sqlite3

def get_region_daily(date):
    conn = sqlite3.connect('./db/covid/test.db')
    cur = conn.cursor()

    sql = 'select * from region where stdDay=? order by incDec desc;'
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows

def get_agender_daily(date):
    conn = sqlite3.connect('./db/covid/test.db')
    cur = conn.cursor()

    sql = 'select * from agender where stdDay=?;'
    cur.execute(sql, (date,))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows