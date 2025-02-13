import pymysql


# 根据故事id插入（绘画prompt， 润色文本， url）
def insert(storyId, prompt, text, url):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "insert into paragraphs values (%s, %s, %s, %s, %s)"
        length = len(prompt)
        for i in range(length):
            cursor.execute(sql, (storyId, prompt[i], text[i], url[i], i.__str__()))
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()


# 根据故事id查找（绘画prompt， 润色文本， url）
# 如果有，返回[(绘画prompt， 润色文本， url), (绘画prompt， 润色文本， url)...], True
# 否则， 返回None, False
def findByStoryId(storyId):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "select * from paragraphs where storyId = %s order by weight asc"
        cursor.execute(sql, storyId)
        result = cursor.fetchall()
        if len(result) == 0:
            return None, False
        res = []
        for row in result:
            res.append(row[1:4])
        return res, True
    except pymysql.MySQLError as e:
        print(e)
        return None, False
    finally:
        cursor.close()
        conn.close()


# 根据故事id修改(绘画prompt，润色文本，url)
def updateByStoryId(storyId, prompt, text, url, weight):
    weight = weight.__str__()
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "update paragraphs set prompt = %s, text = %s, url = %s where storyId = %s and weight = %s"
        cursor.execute(sql, (prompt, text, url, storyId, weight))
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()


# 根据故事id删除记录
def deleteByStoryId(storyId):
    conn = pymysql.connect(host='60.205.122.122', user='xyq', password='xyq123456', database='xyq', charset='utf8mb4', port=3306)
    cursor = conn.cursor()
    try:
        sql = "delete from paragraphs where storyId = %s"
        cursor.execute(sql, storyId)
        conn.commit()
        return True
    except pymysql.MySQLError as e:
        print(e)
        return False
    finally:
        cursor.close()
        conn.close()

