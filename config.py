# "mono:mono@10.106.50.14:3300/parking" 

USER = 'locust'
PASSWORD = 'locust'

# USER = 'sysb'
# PASSWORD = 'sysb'

IP_ADDR = "127.0.0.1"
PORT = 3317
# database name
TS_DB_NAME = "parking"

# False: Create a connection from connection pool. And dosen't use prepare_stmt. 
# True: Create a long connection. Use prepare_stmt.
USE_PREPARE_STMT = True

POOL_SIZE = 300
POOL_RECYCLE = -1
POOL_MAX_OVERFLOW = 0

connection_path = "mariadb+mysqlconnector://" + USER  + ":" + PASSWORD + "@" + IP_ADDR + ":" + str(PORT) + "/" + TS_DB_NAME


# mariadb+mysqlconnector://sysb:sysb@127.0.0.1:3317/test