from flask import Flask, url_for, render_template, session, jsonify, request
import mysql.connector

import json

# idにUUIDを使用する
import uuid

# corsを使う
from flask_cors import CORS

# mysql接続


def mysql_conn():
    conn = mysql.connector.connect(
        db="hatchPost",
        user="root",
        host="localhost",
        port=3306,
    )
    return conn


app = Flask(__name__)

app.secret_key = "secret!"

# CORSの設定
# "http://localhost:3000"をすべてのエンドポイントで許可する
# また、クッキーを含めたリクエストを許可する
CORS(app, resources={
    r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# トップページ


@app.route("/rightProfile", methods=["POST"])
def rightProfile():
    if "userId" in session:

        try:
            conn = mysql_conn()
            cur = conn.cursor()
            cur.execute("""
                        SELECT id, username
                        FROM user
                        WHERE id = %s
                        """, (session["userId"],))
            profileData = cur.fetchone()
            return jsonify({"login":True, "profileData":profileData}), 200
        except Exception as e:
            return jsonify({"login":False, "profileData":("-","Error")}), 400
    else:
        return jsonify({"login": False, "profileData": ("-", "ゲスト")}), 200

@app.route("/newUser", methods=["POST"])
def newUser():
    newUserData = request.get_json()
    print(newUserData)
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        userUuid = str(uuid.uuid4())
        cur.execute("INSERT INTO user(id,username,email,password) VALUES(%s,%s,%s,%s)",
                    (userUuid, newUserData["username"], newUserData["email"], newUserData["password"]))
        conn.commit()
        cur.close()
        conn.close()
        session["userId"] = userUuid
        return jsonify({"message": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error"}), 400


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute("""
                    SELECT id
                    FROM user
                    WHERE email = %s AND password = %s
                    """, (data["email"], data["password"]))

        existCheckUser = cur.fetchone()
        if existCheckUser:
            session["userId"] = existCheckUser[0]
            return jsonify({"state": "success"}), 200
        else:
            return jsonify({"state": "notfound"}), 200
    except:
        return jsonify({"state": "failed"}), 400


@app.route("/newPost", methods=["POST"])
def newPost():
    try:
        postData = request.get_json()
        conn = mysql_conn()
        cur = conn.cursor()
        postUuid = str(uuid.uuid4())
        cur.execute("INSERT INTO post(id,user_id,postContent) VALUES(%s,%s,%s)",
                    (postUuid, session["userId"], postData["postContent"]))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"state": "successful"}), 200
    except Exception as e:
        print(e)
        return jsonify({"state": "filed"})


@app.route("/postData", methods=["POST"])
def postData():
    conn = mysql_conn()
    cur = conn.cursor()
    cur.execute("""
                SELECT user.id, user.username, post.postContent, post.created_at
                FROM post
                INNER JOIN user ON user.id = post.user_id
                """)
    postData = cur.fetchall()
    return jsonify({"state": "success", "postData": postData}), 200

@app.route("/profile", methods=["POST"])
def profile():
    profileUserId = request.get_json()
    print(profileUserId["profileUserId"])
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        # プロフィールデータ
        cur.execute("""
                    SELECT id, username, profileIcon, profileBackImage, profileText
                    FROM user
                    WHERE id = %s
                    """,(profileUserId["profileUserId"],))
        profileData = cur.fetchone()
        # ポストデータ
        cur.execute("""
                    SELECT user.id, user.username, post.postContent, post.created_at
                    FROM post
                    INNER JOIN user ON user.id = post.user_id
                    WHERE post.user_id = %s
                    """,(profileUserId["profileUserId"],))
        postData = cur.fetchall()
        # print(postData)
        # 自分かどうか
        if profileUserId["profileUserId"] == session["userId"]:
            
            return jsonify({"state":"success", "postData":postData, "profileData":profileData, "myself":True}), 200
        else:
            return jsonify({"state":"success", "postData":postData, "profileData":profileData, "myself":False}), 200
    except Exception as e:
        print(e)
        return jsonify({"state":"failed"}), 400

@app.route("/changeProfile", methods=["POST"])
def changeProfile():
    changeProfileData = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute("""
                    UPDATE user
                    SET 
                        username = %s,
                        profileText = %s
                    WHERE id = %s
                    """, (changeProfileData["changeUsername"], changeProfileData["changeProfileText"], session["userId"]))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"state":"success"}), 200
    except Exception as e:
        print(e)
        
        return jsonify({"state":"failed"}), 400

if __name__ == "__main__":
    app.run(debug=True)
