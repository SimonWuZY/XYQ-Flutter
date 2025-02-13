import 'package:flutter/material.dart';

///几个弹窗函数实现需要的弹窗
///@author:Sword
///@data:2024/7/18

// 注册时用到的弹窗
void showDialogLogin(BuildContext context, bool success) {
  showDialog(
    context: context,
    builder: (BuildContext context) {
      return AlertDialog(
        title: success ? const Text("注册成功") : Text("注册失败"),
        content: success
            ? const Icon(Icons.check_circle, color: Colors.green, size: 60.0)
            : const Icon(Icons.cancel, color: Colors.red, size: 60.0),
        actions: [
          TextButton(
            child: const Text("确定"),
            onPressed: () {

              Navigator.of(context).pop();
            },
          ),
        ],
      );
    },
  );
}

// 绘本创作时用到的弹窗
void showResultDialog(BuildContext context, bool isSuccess) {
  showDialog(
    context: context,
    builder: (BuildContext context) {
      return AlertDialog(
        backgroundColor: isSuccess ? Colors.green[100] : Colors.red[100],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isSuccess ? Icons.check_circle : Icons.error,
              color: isSuccess ? Colors.green : Colors.red,
              size: 50,
            ),
            const SizedBox(height: 16),
            Text(
              isSuccess ? "绘本创作完成" : "绘本创作失败请重试",
              style: TextStyle(
                fontSize: 18,
                color: isSuccess ? Colors.green[800] : Colors.red[800],
                fontFamily: 'Heiti',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            child: const Text(
              "确定",
              style: TextStyle(fontSize: 18, fontFamily: 'Heiti'),
            ),
            onPressed: () {
              Navigator.of(context).pop();
            },
          ),
        ],
      );
    },
  );
}

// 查询历史记录时用到的弹窗
void showResultDialogHis(BuildContext context, bool isSuccess) {
  showDialog(
    context: context,
    builder: (BuildContext context) {
      return AlertDialog(
        backgroundColor: isSuccess ? Colors.green[100] : Colors.red[100],
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              isSuccess ? Icons.check_circle : Icons.error,
              color: isSuccess ? Colors.green : Colors.red,
              size: 50,
            ),
            const SizedBox(height: 16),
            Text(
              isSuccess ? "绘本创作完成" : "获取记录失败请重新登录",
              style: TextStyle(
                fontSize: 18,
                color: isSuccess ? Colors.green[800] : Colors.red[800],
                fontFamily: 'Heiti',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            child: const Text(
              "确定",
              style: TextStyle(fontSize: 18, fontFamily: 'Heiti'),
            ),
            onPressed: () {
              Navigator.of(context).pop();
            },
          ),
        ],
      );
    },
  );
}

