import pymysql


# 插入数据
def insert(userName, storyId, saved: str = 'no'):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO user_story (username, storyId, saved) VALUES (%s, %s, %s)"
        cursor.execute(sql, (userName, storyId, saved))
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()


# 根据用户名查找其所有的故事id
def findByUserName(userName):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "SELECT storyId FROM user_story where username = %s and saved = %s"
        cursor.execute(sql, (userName, 'yes'))
        result = cursor.fetchall()
        res = []
        for row in result:
            res.append(row[0])
        return res, True
    except pymysql.MySQLError as e:
        return e, False
    finally:
        cursor.close()
        conn.close()


# 删除对应的故事Id
def deleteByStoryId(storyId):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "delete from user_story where storyId = %s"
        cursor.execute(sql, storyId)
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        return False
    finally:
        cursor.close()
        conn.close()


# 根据故事Id修改状态
def updateByStoryId(storyId, saved):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "update user_story set saved = %s where storyId = %s"
        cursor.execute(sql, (saved, storyId))
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        return False
    finally:
        cursor.close()
        conn.close()
