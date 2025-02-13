
import 'package:aigc_/dao/login_dao.dart';

hiHeader_login(){
  Map<String, String> header ={
    // 用户登录唯一标识
    "boarding-pass": LoginDao.getBoardingPass()??" ",
  };
  return header;
}


hiHeader_signup(){
  Map<String, String> header ={
    'Content-Type':'/users/signup'
  };
  return header;
}