import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('MYSQL_HOST')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
db = os.getenv('MYSQL_DB', 'defaultdb')
port = int(os.getenv('MYSQL_PORT', 3306))

ca_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ca.pem')
ssl_config = {}
if os.path.exists(ca_path):
    ssl_config['ca'] = ca_path

print("Connecting to database...")
try:
    if ssl_config:
        conn = pymysql.connect(host=host, user=user, password=password, database=db, port=port, ssl=ssl_config)
    elif host and 'aivencloud.com' in host:
        conn = pymysql.connect(host=host, user=user, password=password, database=db, port=port, ssl={})
    else:
        conn = pymysql.connect(host=host, user=user, password=password, database=db, port=port)
    
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    print("Tables in database:", tables)
    
    for table_tuple in tables:
        table = table_tuple[0]
        print(f"\nStructure of {table}:")
        cur.execute(f"DESCRIBE {table}")
        columns = cur.fetchall()
        for col in columns:
            print("  ", col)
            
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"  Row count: {count}")
        
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
