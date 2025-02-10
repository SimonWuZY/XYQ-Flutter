import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_hi_cache/flutter_hi_cache.dart';

///此类实现用户信息的获取和更新接口
///userAvatar和userNickname用于保存用户头像和昵称
///在实际测试时请改写Uri中的域名及路径
///@author:Simon
///@date:2024/7/15

class UserDao {
  // 用户信息 key
  static const userAvatar = "user_avatar";
  static const userNickname = "user_nickname";

  // 获取用户信息函数
  static Future<Map<String, String?>> getUserInfo({required String token}) async {
    var uri = Uri.http("localhost:5000", "/users/info");
    final response = await http.get(uri, headers: {'Authorization': 'Bearer $token'});

    if (response.statusCode == 200) {
      var responseData = json.decode(response.body);
      print("User Info: $responseData");

      // 保存用户信息
      _saveUserInfo(responseData['avatar'], responseData['nickname']);

      return {
        'avatar': responseData['avatar'],
        'nickname': responseData['nickname']
      };
    } else {
      print("Failed to fetch user info. Status code: ${response.statusCode}");
      return {'avatar': null, 'nickname': null};
    }
  }

  // 更新用户信息函数
  static Future<bool> updateUserInfo({required String token, String? avatarPath, String? nickname}) async {
    var uri = Uri.http("localhost:5000", "/users/update");

    var request = http.MultipartRequest('POST', uri);
    request.headers['Authorization'] = 'Bearer $token';

    if (avatarPath != null) {
      request.files.add(await http.MultipartFile.fromPath('avatar', avatarPath));
    }
    if (nickname != null) {
      request.fields['nickname'] = nickname;
    }

    final response = await request.send();

    if (response.statusCode == 200) {
      print("User info updated successfully.");
      if (avatarPath != null) {
        _saveUserAvatar(avatarPath);
      }
      if (nickname != null) {
        _saveUserNickname(nickname);
      }
      return true;
    } else {
      print("Failed to update user info. Status code: ${response.statusCode}");
      return false;
    }
  }

  // 保存用户头像
  static void _saveUserAvatar(String value) {
    HiCache.getInstance().setString(userAvatar, value);
  }

  // 保存用户昵称
  static void _saveUserNickname(String value) {
    HiCache.getInstance().setString(userNickname, value);
  }

  // 保存用户信息
  static void _saveUserInfo(String? avatar, String? nickname) {
    if (avatar != null) {
      _saveUserAvatar(avatar);
    }
    if (nickname != null) {
      _saveUserNickname(nickname);
    }
  }

  // 获取用户头像
  static String? getUserAvatar() {
    return HiCache.getInstance().get(userAvatar);
  }

  // 获取用户昵称
  static String? getUserNickname() {
    return HiCache.getInstance().get(userNickname);
  }
}
