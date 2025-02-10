import 'dart:convert';
import 'package:aigc_/dao/http_utils.dart';
import 'package:aigc_/util/navigator_util.dart';
import 'package:flutter_hi_cache/flutter_hi_cache.dart';
import 'package:http/http.dart' as http;

///此类实现登录所需的网络接口及其函数
///boardPass用于保存用户登录令牌
///在实际测试时请改写Uri中的域名及路径
///@author:Sword
///@date:2024/7/3
class LoginDao{
  // 登录 key
  static const boardPass = "boarding_pass";

  // 登录函数
  static Future<int> login({required String userName, required String passWord, required String au_token}) async {
    Map<String, String> paramsMap = {
      'userName': userName,
      'password': passWord,
      'token': au_token,
    };

    String info = json.encode(paramsMap);
    var uri = Uri.http(HttpConfig.ip, "/users/login");
    final http.Response response = await http.post(uri, body: info);

    if (response.statusCode == 200) {
      print("________123______");
      var responseData = json.decode(response.body);
      print("____$responseData");
      // 正确处理响应数据
      if (responseData['message'] == 'login success') {

        // 保存登录令牌
        _saveBoardingPass(responseData['token']);

        return 1;  // 登录成功
      } else {
        return 0;  // 登录失败
      }
    } else {
      print("Failed to login. Status code: ${response.statusCode}");
      return -1;  // 网络或其他错误
    }
  }
  
  // 注册函数
  static Future<bool> signup({required String userName, required String passWord}) async {
    Map<String, String> paramsMap = {};
    paramsMap['userName'] = userName;
    paramsMap['password'] = passWord;
    String info = json.encode(paramsMap);

    // 实现 http 网络请求
    var uri = Uri.http(HttpConfig.ip, "/users/signup");
    final response = await http.post(uri, body: info);
    
    // 输出返回的json内容
    var responseData = json.decode(response.body);
    print("Response JSON: $responseData");

    if(responseData['message'] == 'signup success'){
      return true;
    }else{
      return false;
    }
  }
  
  // 登出函数
  static void logout(){
    print("____移除");
    // 移除登录保存的令牌
    HiCache.getInstance().remove(boardPass);
    print("____跳转");
    // 跳转到登录页
    NavigatorUtil.goToLogin();
    //NavigatorUtil.push(context,LoginPage());
  }

  // 保存令牌
  static void _saveBoardingPass(String value) {
    HiCache.getInstance().setString(boardPass, value);
  }

  // 获取令牌
  static  getBoardingPass() {
    return HiCache.getInstance().get(boardPass);
  }
}