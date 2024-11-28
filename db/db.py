import mysql.connector

conn = mysql.connector.connect(
    host="hatchpost-server.mysql.database.azure.com",
    port=3306,
    user="plmfutylzv",
    password="Yosshi20031013",
    ssl_ca="./DigiCertGlobalRootG2.crt.pem",
    database="hatchpost-database"
)

# conn = mysql.connector.connect(
#     host="localhost",
#     port=3306,
#     user="root",
#     password="",
#     # ssl_ca="./DigiCertGlobalRootG2.crt.pem",
#     database="hatchpost"
# )

cur = conn.cursor()

cur.execute("""
            CREATE TABLE IF NOT EXISTS user(
                id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50),
                email VARCHAR(100) UNIQUE,
                password VARCHAR(50),
                profileIcon VARCHAR(36),
                profileBackImage VARCHAR(36),
                profileText TEXT
            )
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS post (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                postContent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
            """)




cur.execute("""
            CREATE TABLE IF NOT EXISTS heart(
                id VARCHAR(36) PRIMARY KEY,
                post_id VARCHAR(36),
                user_id VARCHAR(36),
                FOREIGN KEY (user_id) REFERENCES user(id),
                FOREIGN KEY (post_id) REFERENCES post(id),
                UNIQUE(user_id, post_id)
            )
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS follow (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                follow_id VARCHAR(36),
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(follow_id) REFERENCES user(id),
                UNIQUE(user_id, follow_id)
            )
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS chatList (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                friend_id VARCHAR(36),
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(friend_id) REFERENCES user(id),
                UNIQUE(user_id, friend_id)
            )
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS chat (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                friend_id VARCHAR(36),
                content Text,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(friend_id) REFERENCES user(id)
            )
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS chatRequest(
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                friend_id VARCHAR(36),
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(friend_id) REFERENCES user(id),
                UNIQUE(user_id, friend_id)
            )
            """)

cur.execute("""
            CREATE TABLE IF NOT EXISTS comment(
                id VARCHAR(36) PRIMARY KEY,
                post_id VARCHAR(36),
                user_id VARCHAR(36),
                commentContent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(post_id) REFERENCES post(id)
            )
            """)

cur.execute("SHOW TABLES")
tables = cur.fetchall()

print("データベース内のテーブル一覧:")
for table in tables:
    print(table[0])

# cur.execute("""
#             SELECT *
#             FROM user
#             """)

# list = cur.fetchall()
# print(list)

conn.commit()