import 'package:flutter/material.dart';

// 登录按钮的widget
// 禁用功能的按钮
class LoginButton extends StatelessWidget {
  final String title;
  final bool enable;
  
  // 回调函数
  // VoidCallback 回调函数之一 不用于传递值
  final VoidCallback? onPressed;
  
  // 给予默认值或不需要显示传值的参数 需要在({})之间
  // 不在{}之中的参数是必须在函数调用时显示传值的
  // 别忘了继承传值
  const LoginButton(this.title,{ this.enable = true,this.onPressed,super.key});

  @override
  Widget build(BuildContext context) {
    // MaterialButton 实现水波纹效果的按钮
    return MaterialButton(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
      height: 45,
      // 通过 enable 表示按钮状态 禁用 or 可点击 
      // enable 为 true 传递 onPressed 为 false 传递 null
      onPressed: enable ? onPressed : null,
      // 传递 null 禁用按钮
      // 设置禁用下的颜色效果
      disabledColor: Color.fromARGB(255, 223, 206, 206),
      color: Colors.orange,
      child: Text(
          title,
          style: const TextStyle(color: Colors.white, fontSize: 25,fontFamily: 'heiti'),
      ),
    );
  }
}