bool isNotEmpty(String? text){
  return text?.isNotEmpty ?? false;
}

bool isEmpty(String? text){
  return text?.isEmpty ?? true;
}

// 验证用户名的正则表达式
bool isValidUserName(String userName) {
  final RegExp userNameRegExp = RegExp(r'^[a-zA-Z0-9]{6,20}$'); // 6-20位的字母或数字
  return userNameRegExp.hasMatch(userName);
}

// 验证密码的正则表达式
bool isValidPassword(String password) {
  final RegExp passWordRegExp = RegExp(r'^[a-zA-Z0-9@#$%^&*]{8,20}$'); // 8-20位的字母、数字或特殊字符
  return passWordRegExp.hasMatch(password);
}
