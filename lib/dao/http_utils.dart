import 'package:aigc_/dao/login_dao.dart';
import 'package:aigc_/util/story_page.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

///统一设置相应的IP和端口
class HttpConfig {
  static const ip = "60.205.122.122:1888";
}

///传递故事大纲函数
///传递信息： outline + token
///接受信息： message + id
///@author:Sword
///2024/7/16
Future<Map<String, String>?> set_outline(String text) async {
  Map<String, String> paramsMap = {};
  paramsMap['outline'] = text;
  paramsMap['token'] = LoginDao.getBoardingPass();

  Map<String, String> result = {};

  String info = json.encode(paramsMap);

  var uri = Uri.http(HttpConfig.ip, "/story/generateStory");
  final http.Response response = await http.post(uri, body: info);

  if (response.statusCode == 200) {
    print("生成故事_________response.statusCode = ${response.statusCode}");

    var responseData = jsonDecode(response.body);
    print("生成故事_________response.body = ${responseData}");

    // 处理返回的 json
    if (responseData['message'] == 'true') {
      result['storyId'] = responseData['storyId'];
      return result;
    } else {
      return null;
    }
  } else {
    print("Failed to set outline. Status code: ${response.statusCode}");
    return null;
  }
}

///获取绘本图片和文本函数
///传递信息： token + storyId
///接受信息： message + texts + urls
///@author:Sword
///2024/7/16
Future<List<StoryPage>?> getPics(String storyId) async {
  Map<String, String> paramsMap = {};
  paramsMap['storyId'] = storyId;
  paramsMap['token'] = LoginDao.getBoardingPass();

  String info = json.encode(paramsMap);
  print("______________________发送获取绘本请求");
  var uri = Uri.http(HttpConfig.ip, "/story/getByStoryId");
  final http.Response response = await http.post(uri, body: info);

  if (response.statusCode == 200) {
    print("接受故事_________response.statusCode = ${response.statusCode}");

    var responseData = jsonDecode(response.body);
    print("接受故事_________response.body = ${responseData}");

    // 处理返回的 json
    if (responseData['message'] == 'true') {
      List<String> texts = List<String>.from(responseData['texts']);
      print("______${texts.length}");
      List<String> images = List<String>.from(responseData['urls']);
      List<StoryPage> result = [];
      for (int i = 0; i < texts.length; i++) {
        result.add(StoryPage(imageUri: images[i], text: texts[i]));
        print("_______________________绘本容量$i");
      }
      print("______________________准备返回$result");
      return result;
    }
    return null;
  } else {
    print("Failed to get storys. Status code: ${response.statusCode}");
    return null;
  }
}

///修改当前页绘本图片函数
///传递信息： token + storyId + current
///接受信息： newPage
///@author:Sword
///2024/7/16
Future<String?> update_current(String storyId, String current) async {
  Map<String, String> paramsMap = {};
  paramsMap['storyId'] = storyId;
  paramsMap['token'] = LoginDao.getBoardingPass();
  // 当前用户需要修改的页数
  paramsMap['current'] = current;

  String result = "";

  String info = json.encode(paramsMap);

  var uri = Uri.http(HttpConfig.ip, "/story/updateCurrentPicture");
  final http.Response response = await http.post(uri, body: info);

  if (response.statusCode == 200) {
    print("单页置换故事_________response.statusCode = ${response.statusCode}");

    var responseData = jsonDecode(response.body);
    print("单页置换故事_________response.body = ${responseData}");

    // 处理返回的 json
    if (responseData['message'] == 'true') {
      result = responseData['newPage'];
      return result;
    } else {
      return null;
    }
  } else {
    print("Failed to refresh Picture. Status code: ${response.statusCode}");
    return null;
  }
}

///修改整个绘本重画函数
///传递信息： token + storyId + requirement
///接受信息： storyId
///@author:Sword
///2024/7/16
Future<String?> generate_new_story(String storyId, String requirement) async {
  Map<String, String> paramsMap = {};
  paramsMap['storyId'] = storyId;
  paramsMap['token'] = LoginDao.getBoardingPass();
  // 当前用户提出的修改要求
  paramsMap['requirement'] = requirement;

  String result = "";

  String info = json.encode(paramsMap);

  var uri = Uri.http(HttpConfig.ip, "/story/generateNewStory");
  final http.Response response = await http.post(uri, body: info);

  if (response.statusCode == 200) {
    print("整体重画故事_________response.statusCode = ${response.statusCode}");

    var responseData = jsonDecode(response.body);
    print("整体重画故事_________response.body = ${responseData}");

    // 处理返回的 json
    if (responseData['message'] == 'true') {
      result = responseData['storyId'];
      return result;
    } else {
      return null;
    }
  } else {
    print(
        "Failed to rechange the whole Picture. Status code: ${response.statusCode}");
    return null;
  }
}

///保存绘本函数
///传递信息： token + storyId
///接受信息： /
///@author:Sword
///2024/7/16
Future<bool?> save_story(String storyId) async {
  Map<String, String> paramsMap = {};
  paramsMap['storyId'] = storyId;
  paramsMap['token'] = LoginDao.getBoardingPass();

  String info = json.encode(paramsMap);

  var uri = Uri.http(HttpConfig.ip, "/story/saveStory");
  final http.Response response = await http.post(uri, body: info);

  if (response.statusCode == 200) {
    print("保存绘本_________response.statusCode = ${response.statusCode}");

    var responseData = jsonDecode(response.body);
    print("保存绘本_________response.body = ${responseData}");

    // 处理返回的 json
    if (responseData['message'] == 'true') {
      return true;
    }
  } else {
    print(
        "Failed to save the whole Picture. Status code: ${response.statusCode}");
    return false;
  }
  return false;
}

///删除绘本函数
///传递信息： token + storyId
///接受信息： /
///@author:Sword
///2024/7/16
Future<bool?> delete_story(String storyId) async {
  Map<String, String> paramsMap = {};
  paramsMap['storyId'] = storyId;
  paramsMap['token'] = LoginDao.getBoardingPass();

  String info = json.encode(paramsMap);

  var uri = Uri.http(HttpConfig.ip, "/story/deleteStory");
  final http.Response response = await http.post(uri, body: info);

  if (response.statusCode == 200) {
    print("删除绘本_________response.statusCode = ${response.statusCode}");

    var responseData = jsonDecode(response.body);
    print("删除绘本_________response.body = ${responseData}");

    // 处理返回的 json
    if (responseData['message'] == 'true') {
      return true;
    }
  } else {
    print(
        "Failed to delete the whole Picture. Status code: ${response.statusCode}");
    return false;
  }
  return null;
}

///历史绘本展示所有绘本封面函数
///传递信息： token
///接受信息： title + cover + storyid
///@author:Sword
///2024/7/16
Future<List<StoryPageId>?> get_all_story() async {
  Map<String, String> paramsMap = {};
  paramsMap['token'] = LoginDao.getBoardingPass();

  List<StoryPageId> result = [];

  String info = json.encode(paramsMap);

  var uri = Uri.http(HttpConfig.ip, "/story/getAllStory");
  final http.Response response = await http.post(uri, body: info);

  if (response.statusCode == 200) {
    print("获取历史绘本封面_________response.statusCode = ${response.statusCode}");

    var responseData = jsonDecode(response.body);
    print("获取历史绘本封面_________response.body = ${responseData}");

    // 处理返回的 json
    if (responseData['message'] == 'true') {
      List<String> titles = List<String>.from(responseData['title']);
      print("______${titles.length}");
      List<String> covers = List<String>.from(responseData['cover']);
      List<String> storyIds = List<String>.from(responseData['storyId']);
      for (int i = 0; i < titles.length; i++) {
        result.add(StoryPageId(
            imageUri: covers[i], text: titles[i], storyId: storyIds[i]));
        print("_______________________封面容量$i");
      }
      print("________准备返回$result");
      return result;
    } else {
      return null;
    }
  } else {
    print(
        "Failed to get the historical Pictures. Status code: ${response.statusCode}");
    return null;
  }
}
