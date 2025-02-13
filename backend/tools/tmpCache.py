from diskcache import Cache

cache = Cache('./tmpFile/cache')


def setCache(key, value):
    cache.set(key, value, expire=3600)


def getCache(key):
    return cache.get(key)


def setTaskCache(storyId, res):
    dict = {"Status": "generating", "storyId": storyId, "texts": None, "urls": None}
    dict["texts"] = res[3]
    dict["urls"] = ["" for _ in range(len(res[3]))]
    dict["urls"][0] = res[4][0]
    setCache(storyId, dict)
    print("Cache Successfully: ", cache.get(storyId))
    return dict


def setUrl(storyId, url, index):
    dict = getCache(storyId)
    dict["urls"][index] = url
    setCache(storyId, dict)
    return dict


def setUrls(storyId, urls):
    dict = getCache(storyId)
    dict["urls"] = urls
    setCache(storyId, dict)
    return dict


def finishTask(storyId):
    dict = getCache(storyId)
    dict["Status"] = "finished"
    setCache(storyId, dict)
    return dict


def getTaskCache(storyId):
    dict = getCache(storyId)
    return dict