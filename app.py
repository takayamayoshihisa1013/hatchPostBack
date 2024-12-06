from flask import Flask, url_for, render_template, session, jsonify, request
from flask_session import Session
import mysql.connector
import os
# idにUUIDを使用する
import uuid
# corsを使う
from flask_cors import CORS

from datetime import timedelta

# mysql接続
# mysql接続
def mysql_conn():

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
    return conn


app = Flask(__name__)
app.debug = True

# Flask-Session設定
app.config["SECRET_KEY"] = "yosshi20031013"
app.config['SESSION_COOKIE_NAME'] = 'kotodama_Cookie'
app.config["SESSION_TYPE"] = "filesystem"  # ファイルベースのセッション管理
app.config["SESSION_FILE_DIR"] = os.path.join(os.getcwd(), "flask_session")  # 保存場所
app.config["SESSION_PERMANENT"] = False  # 永続セッション
app.config["SESSION_USE_SIGNER"] = True  # セッションを署名付きで保護
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # クロスサイト間でのクッキー共有を許可
app.config["SESSION_COOKIE_SECURE"] = True
Session(app)

# 保存ディレクトリを作成
os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

# CORSの設定
# "http://localhost:3000"をすべてのエンドポイントで許可する
# また、クッキーを含めたリクエストを許可する
# CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)
CORS(app, resources={
    r"/*": {"origins": "https://ambitious-cliff-09a302f00.4.azurestaticapps.net"}}, supports_credentials=True)


# 左側のプロフィール
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
            return jsonify({"login": True, "profileData": profileData}), 200
        except Exception as e:
            print("error:" + str(e))
            return jsonify({"login": False, "profileData": ("-", "Error")}), 400
    else:
        return jsonify({"login": False, "profileData": ("-", "ゲスト")}), 200

# ユーザー登録
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
        print("error:" + str(e))
        return jsonify({"message": "error", "error": str(e)}), 400

# ログイン
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
            
            print("userID:" + session["userId"])
            return jsonify({"state": "success"}), 200
        else:
            print("userID:" + "database not found")
            return jsonify({"state": "notfound"}), 200
    except Exception as e:
        print("error:" + str(e))
        return jsonify({"state": "failed"}), 400

# ログアウト
@app.route("/logout", methods=["POST"])
def logout():
    try:
        session.clear()
        return jsonify()
    except Exception as e:
        return jsonify({"error": "error" + str(e)})

# ポスト投稿
@app.route("/newPost", methods=["POST"])
def newPost():
    postContent = request.form.get("postContent")
    imageList = request.files
    print(imageList, postContent)
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        postUuid = str(uuid.uuid4())
        cur.execute("INSERT INTO post(id,user_id,postContent) VALUES(%s,%s,%s)",
                    (postUuid, session["userId"], postContent))
        UPLOAD_FOLDER = "./src/images"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"state": "successful"}), 200
    except Exception as e:
        print("error:" + str(e))
        return jsonify({"state": "filed"}), 400

# ポストデータ


@app.route("/postData", methods=["POST"])
def postData():
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        print(f"session:{dict(session)}")
        # ポストデータ
        if "userId" in session:
            print(session["userId"])
            cur.execute("""
                        SELECT 
                            user.id AS user_id, 
                            user.username, 
                            post.postContent, 
                            post.created_at,
                            post.id AS post_id,
                            COALESCE(COUNT(heart.post_id), 0) AS heart_count,
                            CASE 
                                WHEN EXISTS (
                                    SELECT 1 
                                    FROM heart 
                                    WHERE heart.post_id = post.id AND heart.user_id = %s
                                ) THEN 1
                                ELSE 0
                            END AS is_liked
                        FROM post
                        INNER JOIN user ON user.id = post.user_id
                        LEFT JOIN heart ON post.id = heart.post_id
                        GROUP BY post.id, user.id, user.username, post.postContent, post.created_at
                        ORDER BY post.created_at DESC;
                        """, (session["userId"],))
            postData = cur.fetchall()
        else:
            cur.execute("""
                        SELECT 
                            user.id AS user_id, 
                            user.username, 
                            post.postContent, 
                            post.created_at,
                            post.id AS post_id,
                            COALESCE(COUNT(heart.post_id), 0) AS heart_count
                        FROM post
                        INNER JOIN user ON user.id = post.user_id
                        LEFT JOIN heart ON post.id = heart.post_id
                        GROUP BY post.id, user.id, user.username, post.postContent, post.created_at
                        ORDER BY post.created_at DESC;
                        """)
            postData = cur.fetchall()
        print(os.listdir(app.config["SESSION_FILE_DIR"]), "cookie")
        return jsonify({"state": "success", "postData": postData}), 200
    except Exception as e:
        print("error:" + str(e))
        return jsonify({"state": "success", "postData": [], "error":str(e)}), 400

# いいね処理
@app.route("/heart", methods=["POST"])
def heart():
    data = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute("""
                    SELECT id
                    FROM heart
                    WHERE user_id = %s AND post_id = %s
                    """, (session["userId"], data["postId"]))
        heartExist = cur.fetchone()
        if heartExist:
            cur.execute("""
                        DELETE
                        FROM heart
                        WHERE id = %s
                        """, (heartExist[0],))
        else:
            heartUuid = str(uuid.uuid4())
            cur.execute("INSERT INTO heart(id,post_id,user_id) VALUES(%s,%s,%s)",
                        (heartUuid, data["postId"], session["userId"]))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"state": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"state": "failed"}), 400

# プロフィールデータ


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
                    """, (profileUserId["profileUserId"],))
        profileData = cur.fetchone()
        # フォロー・フォロワーデータ
        cur.execute("""
                    SELECT
                        COUNT(CASE WHEN user_id = %s THEN 1 ELSE NULL END) AS follow_count,
                        COUNT(CASE WHEN follow_id = %s THEN 1 ELSE NULL END) AS follower_count
                    FROM follow
                """, (profileUserId["profileUserId"], profileUserId["profileUserId"]))
        followData = cur.fetchone()
        # ポストデータ
        cur.execute("""
                    SELECT user.id, user.username, post.postContent, post.created_at
                    FROM post
                    INNER JOIN user ON user.id = post.user_id
                    WHERE post.user_id = %s
                    """, (profileUserId["profileUserId"],))
        postData = cur.fetchall()
        # ログインしているか
        if "userId" in session:
            # 自分かどうか
            if profileUserId["profileUserId"] != session["userId"]:
                # フォローしているかどうか
                cur.execute("""
                            SELECT *
                            FROM follow
                            WHERE user_id = %s AND follow_id = %s
                            """, (session["userId"], profileUserId["profileUserId"]))
                followStateCheck = cur.fetchone()
                # フォロー存在確認
                if followStateCheck:
                    return jsonify({"state": "success", "postData": postData, "profileData": profileData, "myself": False, "followState": True, "followData": followData}), 200
                else:
                    return jsonify({"state": "success", "postData": postData, "profileData": profileData, "myself": False, "followState": False, "followData": followData}), 200
            else:
                return jsonify({"state": "success", "postData": postData, "profileData": profileData, "myself": True, "followState": "myself", "followData": followData}), 200
        # ログインしていなかった場合
        else:
            return jsonify({"state": "success", "postData": postData, "profileData": profileData, "myself": False, "followState": "notLogin", "followData": followData}), 200
    except Exception as e:
        print(e)
        return jsonify({"state": "failed"}), 400

# プロフィール変更


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
        return jsonify({"state": "success"}), 200
    except Exception as e:
        print(e)

        return jsonify({"state": "failed"}), 400

# フォロー


@app.route("/follow", methods=["POST"])
def follow():
    followData = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute("""
                    SELECT id
                    FROM follow
                    WHERE user_id = %s AND follow_id = %s
                    """, (session["userId"], followData["followId"]))
        followId = cur.fetchone()
        if followId:
            cur.execute("""
                        DELETE 
                        FROM follow
                        WHERE id = %s
                        """, (followId[0],))
        else:
            followUuid = str(uuid.uuid4())
            cur.execute("INSERT INTO follow(id,user_id,follow_id) VALUES(%s,%s,%s)",
                        (followUuid, session["userId"], followData["followId"]))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"state": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"state": "failed"}), 400

# フォロー・フォロワーデータ


@app.route("/followList", methods=["POST"])
def followList():
    followIdData = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        # フォローデータ
        cur.execute("""
                    SELECT follow.follow_id, user.username, user.profileText, user.profileIcon
                    FROM follow
                    INNER JOIN user ON user.id = follow.follow_id
                    WHERE user_id = %s
                    """, (followIdData["followId"],))
        followList = cur.fetchall()
        # フォロワーデータ
        cur.execute("""
                    SELECT follow.user_id, user.username, user.profileText, user.profileIcon
                    FROM follow
                    INNER JOIN user ON user.id = follow.user_id
                    WHERE follow_id = %s
                    """, (followIdData["followId"],))
        followerList = cur.fetchall()
        print(followList, followerList)
        return jsonify({"state": "success", "followList": followList, "followerList": followerList}), 200
    except Exception as e:
        print(e)
        return jsonify({"state": "failed", "followList": False, "followerList": False}), 400

# チャットの追加


@app.route("/makeNewChat", methods=["POST"])
def makeNewChat():
    data = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        # チャットが存在するかの確認
        cur.execute("""
                    SELECT *
                    FROM chatList
                    WHERE user_id = %s AND friend_id = %s
                    """, (session["userId"], data["friendId"]))
        chatExistCheck = cur.fetchone()
        if not chatExistCheck:
            # 存在しなかったら追加
            chatUuid = str(uuid.uuid4())
            cur.execute("INSERT INTO chatList(id,user_id,friend_id) VALUES(%s,%s,%s)",
                        (chatUuid, session["userId"], data["friendId"]))
            conn.commit()
            cur.close()
            conn.close()

        return jsonify({"state": "success"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": e}), 400

# チャットデータ


@app.route("/chat", methods=["POST"])
def chat():
    my = session["userId"]
    data = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute("""
                    SELECT user.id, user.username, user.profileIcon, chat.content
                    FROM chat
                    INNER JOIN user ON user.id = chat.user_id 
                    WHERE (chat.user_id = %s AND chat.friend_id = %s) OR (chat.user_id = %s AND chat.friend_id = %s)
                    ORDER BY chat.created_at ASC
                    """, (my, data["friendId"], data["friendId"], my))
        chatData = cur.fetchall()

        # 新しく自分かどうかを含めたデータを作る
        newChatData = []
        for row in chatData:
            if row[0] == my:
                newChatData.append((row + ("my",)))
            else:
                newChatData.append((row + ("friend",)))
        print(chatData)

        return jsonify({"state": "success", "chatData": newChatData}), 200
    except Exception as e:
        print(e)
        return jsonify({}), 400


@app.route("/chatListData", methods=["POST"])
def chatListData():
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        cur.execute("""
                    SELECT 
                        chatList.friend_id, 
                        user.username,
                        user.profileText
                    FROM chatList
                    INNER JOIN user ON user.id = chatList.user_id
                    WHERE user_id = %s OR friend_id = %s
                    """, (session["userId"], session["userId"]))
        chatListData = cur.fetchall()
        # print(chatListData[1])
        return jsonify({"chatListData": chatListData}), 200
    except Exception as e:
        print(e)
        return jsonify({}), 400

# 新しいチャットのコメント


@app.route("/newChatContent", methods=["POST"])
def newChatContent():
    data = request.get_json()
    print(data)
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        chatUuid = str(uuid.uuid4())
        cur.execute("INSERT INTO chat(id,user_id,friend_id,content) VALUES(%s,%s,%s,%s)",
                    (chatUuid, session["userId"], data["friendId"], data["newChatContent"]))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({}), 200
    except Exception as e:
        print(e)
        return jsonify({})


@app.route("/comment", methods=["POST"])
def comment():
    data = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        # コメントされてるポスト
        cur.execute("""
                    SELECT user.id, user.username, post.postContent, post.created_at
                    FROM post
                    INNER JOIN user ON user.id = post.user_id
                    WHERE post.id = %s
                    """, (data["postId"],))
        subjectPost = cur.fetchone()
        # ポストに対するコメント一覧
        cur.execute("""
                    SELECT user.id, user.username, user.profileIcon, comment.commentContent, comment.created_at
                    FROM comment
                    INNER JOIN user ON user.id = comment.user_id
                    INNER JOIN post ON post.id = comment.post_id
                    WHERE comment.post_id = %s
                    ORDER BY comment.created_at ASC
                    """, (data["postId"],))
        commentData = cur.fetchall()
        return jsonify({"state": "success", "commentData": commentData, "subjectPost": subjectPost}), 200
    except Exception as e:
        print(e)
        return jsonify({"state": "failed", "error": str(e)}), 400


@app.route("/newComment", methods=["POST"])
def newComment():
    data = request.get_json()
    try:
        conn = mysql_conn()
        cur = conn.cursor()
        commentUuid = str(uuid.uuid4())
        # コメント追加
        cur.execute("INSERT INTO comment(id,post_id,user_id,commentContent) VALUES(%s,%s,%s,%s)",
                    (commentUuid, data["postId"], session["userId"], data["commentContent"]))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({}), 200
    except Exception as e:
        print(e)
        return jsonify({"state": "failed", "error": str(e)}), 400


@app.route("/test")
def test():
    return "test"

@app.route("/sendTest", methods=["POST", "OPTIONS"])
def sendTest():
    print(request.cookies)
    return jsonify({"happy":"happy"}), 200


if __name__ == "__main__":
    app.run(debug=True)
