import 'package:flutter/material.dart';

// 登录输入框  自定义widget
class InputWidget extends StatelessWidget {
  final String hint;

  // 回调函数 泛型
  // ValueChanged 常用两个回调函数之一 主要用于传递值
  final ValueChanged<String>? onChanged;
  final bool obsureText;

  // 键盘输入类型
  final TextInputType? keyboardType;

  // final 参数必须在构造时显性赋值
  const InputWidget(this.hint,
      {super.key, this.onChanged, this.obsureText = false, this.keyboardType});

  @override
  Widget build(BuildContext context) {
    // 上下结构
    return Column(
      children: [
        _input(),
        // 实现分割线
        // const Divider(
        //     color: Colors.black,
        //     height: 0.5,
        //     thickness: 1,
        // )
      ],
    );
  }

  // 提取方法
  _input() {
    // 使用 TextField 组件
    return TextField(
      // 同一个类中的方法 访问类中变量不需要用 this.
      onChanged: onChanged,
      obscureText: obsureText,
      keyboardType: keyboardType,
      // 优先获取焦点
      // 用户名优先得到光标
      autofocus: !obsureText,
      cursorColor: Colors.blueAccent,
      style: const TextStyle(
          fontSize: 17, color: Colors.black54, fontWeight: FontWeight.w400),
      // 输入框样式
      decoration: InputDecoration(
          border: InputBorder.none,
          // 默认提示文字
          hintText: hint,
          hintStyle: const TextStyle(fontSize: 17, color: Colors.black26)),
    );
  }
}
