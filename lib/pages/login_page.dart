import 'package:aigc_/dao/login_dao.dart';
import 'package:aigc_/widget/result_dialog.dart';
import 'package:gap/gap.dart';
import 'package:aigc_/util/navigator_util.dart';
import 'package:aigc_/util/string_util.dart';
import 'package:aigc_/widget/input_widget.dart';
import 'package:aigc_/widget/login_widget.dart';
import 'package:flutter/material.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  // 控制登录按钮是否可用
  bool loginEnable = false;

  // 用户登录所需数据
  String? userName;
  String? passWord;
  String au_token = '';

  // 验证用户名的正则表达式
  bool isValidUserName(String userName) {
    final RegExp userNameRegExp = RegExp(r'^[a-zA-Z0-9]{6,20}$'); // 6-20位的字母或数字
    return userNameRegExp.hasMatch(userName);
  }

  // 验证密码的正则表达式
  bool isValidPassword(String password) {
    final RegExp passWordRegExp =
        RegExp(r'^[a-zA-Z0-9@#$%^&*]{8,20}$'); // 8-20位的字母、数字或特殊字符
    return passWordRegExp.hasMatch(password);
  }

  @override
  Widget build(BuildContext context) {
    NavigatorUtil.updateContext(context);
    return Scaffold(
      // 解决键盘弹起影响页面问题
      resizeToAvoidBottomInset: false,
      body: Stack(
        children: [
          ..._background(),
          ..._content(),
        ],
      ),
    );
  }

  List<Widget> _background() {
    return [
      Positioned.fill(
          child: Image.asset(
        "images/background.png",
        fit: BoxFit.cover,
      )),
      Positioned.fill(child: Container(decoration: const BoxDecoration())),
    ];
  }

  List<Widget> _content() {
    return [
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 25),
        child: ListView(
          children: [
            const Gap(120),
            const Text(
              "欢迎登录星语桥",
              style: TextStyle(
                  fontSize: 40, color: Colors.black54, fontFamily: 'heiti'),
            ),
            const Gap(20),
            const Text(
              "账号密码登录",
              style: TextStyle(
                  fontSize: 20, color: Colors.black54, fontFamily: 'heiti'),
            ),
            Gap(10),
            InputWidget(
              "请输入用户名",
              onChanged: (text) {
                userName = text;
                _checkInput();
              },
            ),
            const Gap(10),
            InputWidget(
              "请输入密码",
              obsureText: true,
              onChanged: (text) {
                passWord = text;
                _checkInput();
              },
            ),
            const Gap(25),
            LoginButton(
              "登录",
              onPressed: () => _login(context),
              enable: loginEnable,
            ),
            const Gap(15),
            Align(
              alignment: Alignment.centerRight,
              child: InkWell(
                onTap: () => _showRegistrationDialog(context),
                child: const Text(
                  "注册账号",
                  style: TextStyle(
                    fontSize: 20,
                    color: Colors.orange,
                    fontFamily: 'heiti',
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    ];
  }

  // 检测用户输入格式
  _checkInput() {
    bool enable;
    if (isNotEmpty(userName) && isNotEmpty(passWord)) {
      if (isValidUserName(userName!) && isValidPassword(passWord!)) {
        enable = true;
      } else {
        enable = false;
      }
    } else {
      enable = false;
    }
    setState(() {
      loginEnable = enable;
    });
  }

  _showAlertDialog(String title, String content) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(title),
          content: Text(content),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text("确定"),
            ),
          ],
        );
      },
    );
  }

  _login(context) async {
    try {
      Future<int> result = LoginDao.login(
          userName: userName!, passWord: passWord!, au_token: au_token);
      int value = await result;
      print("value = $value");
      if (value == 1) {
        print("开始登陆！");
        //NavigatorUtil.push(context, const TabNavigator());
        NavigatorUtil.goToHome(context);
      }
    } catch (e) {
      print(e);
    }
  }

  _showRegistrationDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        String? registerUserName;
        String? registerPassWord;
        String? confirmPassword;
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: Color.fromARGB(255, 163, 178, 248), // 设置背景颜色
              title: const Text("成为“星语桥”用户",
                  style: TextStyle(
                      color: Colors.white, fontFamily: 'heiti')), // 设置标题颜色
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  InputWidget(
                    "请输入账号(6-20位字母或数字)",
                    onChanged: (text) {
                      registerUserName = text;
                    },
                  ),
                  InputWidget(
                    "请输入密码(8-20位字母或数字)",
                    obsureText: true,
                    onChanged: (text) {
                      registerPassWord = text;
                    },
                  ),
                  InputWidget(
                    "请确认密码(8-20位字母或数字)",
                    obsureText: true,
                    onChanged: (text) {
                      confirmPassword = text;
                    },
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text("取消",
                      style: TextStyle(
                          color: Colors.white,
                          fontFamily: 'heiti')), // 设置按钮文字颜色
                ),
                TextButton(
                  onPressed: () async {
                    if (isNotEmpty(registerUserName) &&
                        isNotEmpty(registerPassWord)) {
                      if (!isValidUserName(registerUserName!)) {
                        _showAlertDialog("错误", "用户名格式不正确");
                        return;
                      }
                      if (!isValidPassword(registerPassWord!)) {
                        _showAlertDialog("错误", "密码格式不正确");
                        return;
                      }
                      if (registerPassWord != confirmPassword) {
                        _showAlertDialog("警告", "密码不一致，请重新输入");
                      } else {
                        var result = await LoginDao.signup(
                          userName: registerUserName!,
                          passWord: registerPassWord!,
                        );
                        if (result) {
                          Navigator.of(context).pop();
                          showDialogLogin(context, true);
                          print("注册成功！");
                        } else {
                          Navigator.of(context).pop();
                          showDialogLogin(context, false);
                          print("注册失败！");
                        }
                      }
                    }
                  },
                  child: const Text("注册",
                      style: TextStyle(
                          fontSize: 15,
                          color: Colors.white,
                          fontFamily: 'heiti')), // 设置按钮文字颜色
                ),
              ],
            );
          },
        );
      },
    );
  }


}
