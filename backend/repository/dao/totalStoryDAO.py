import pymysql


# 插入数据
def insert(storyId, outline, originalStory):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO total_story VALUES (%s, %s, %s)"
        cursor.execute(sql, (storyId, outline, originalStory))
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()


# 根据故事id查找对应的大纲和故事文本
def findByStoryId(storyId):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "SELECT outline, originalStory FROM total_story where storyId = %s"
        cursor.execute(sql, storyId)
        result = cursor.fetchall()
        if len(result) == 0:
            return None, False
        res = []
        return [result[0][0], result[0][1]], True
    except pymysql.MySQLError as e:
        return e, False
    finally:
        cursor.close()
        conn.close()


# 根据故事id删除数据
def deleteByStoryId(storyId):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "delete from total_story where storyId = %s"
        cursor.execute(sql, storyId)
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        return False
    finally:
        cursor.close()
        conn.close()


# 根据故事id修改数据
def updateByStoryId(storyId, outline, originalStory):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "update total_story set outline = %s, originalStory = %s where storyId = %s"
        cursor.execute(sql, (outline, originalStory, storyId))
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        return False
    finally:
        cursor.close()
        conn.close()



