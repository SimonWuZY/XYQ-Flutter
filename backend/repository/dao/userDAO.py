import pymysql


class User:
    def __init__(self, username, password, avatar):
        self.username = username
        self.password = password
        self.avatar = avatar


def insert(user):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO users (name, password) VALUES (%s, %s)"
        cursor.execute(sql, (user.username, user.password))
        conn.commit()
        return "OK"
    except pymysql.MySQLError as e:
        print(e)
        if e.args[0] == 1062:
            return "already exists"
        else:
            return "error"
    finally:
        cursor.close()
        conn.close()

def findByName(name):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "SELECT * FROM users WHERE name = %s"
        cursor.execute(sql, name)
        res = cursor.fetchone()
        # print(res)
        if res:
            return res, True
        else:
            return "Not Found", False
    except pymysql.MySQLError as e:
        return f"Error: {e}", False
    finally:
        cursor.close()
        conn.close()


def update(user):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "UPDATE users SET password = %s, avatar = %s WHERE name = %s"
        cursor.execute(sql, (user.password, user.avatar, user.username))
        conn.commit()
        return "Success", True
    except pymysql.MySQLError as e:
        return f"Error: {e}", False
    finally:
        cursor.close()
        conn.close()
