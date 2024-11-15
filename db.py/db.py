import mysql.connector

conn = mysql.connector.connect(
    db="hatchPost",
    user="root",
    host="localhost",
    port=3306, 
)

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
            CREATE TABLE IF NOT EXISTS follow (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36),
                follow_id VARCHAR(36),
                FOREIGN KEY(user_id) REFERENCES user(id),
                FOREIGN KEY(follow_id) REFERENCES user(id),
                UNIQUE(user_id, follow_id)
            )
            """)

conn.commit()