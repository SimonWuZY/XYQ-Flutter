import 'package:aigc_/navigator/tab_navigator.dart';
import 'package:aigc_/pages/login_page.dart';
import 'package:aigc_/pages/pic_book.dart';
import 'package:aigc_/pages/pic_book_show.dart';
import 'package:flutter/material.dart';

// 跳转使用工具
class NavigatorUtil{
  // 用于在获取不到 context 的地方,如 dao 中跳转页面时使用, 需要在首页中赋值
  static BuildContext? _context;

  static updateContext(BuildContext context){
    NavigatorUtil._context = context;

    // ignore: avoid_print
    print('init:$_context');
  }

  // 跳转到指定页面
  static void push(BuildContext context, Widget page) {
    print('_____________________Navigating to new page');
    Navigator.of(context).push(MaterialPageRoute(builder: (context) => page));
  }

  // 跳转到首页
  static goToHome(context){
    // 跳转到首页
    print('_____________________homepage跳转');
    Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (context) => const TabNavigator())); 
  }

  // 跳转到登录页
  static goToLogin(){
    // 跳转到 login_page 
    // 如果此处 context 为空说明在当前页初始化 context 发生问题
    print('_____________________logout 跳转');
    Navigator.pushReplacement(
      _context!, MaterialPageRoute(builder: (context) => const LoginPage())); 
  }

  // 跳转到绘本展示页
  // 需要额外传递绘本Id
  static void goToPic(BuildContext context, String storyId, bool forceLandscape) {
    print('_____________________Pic 跳转');
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PicBook(storyId: storyId,forceLandscape: forceLandscape),
      ),
    );
  }

  // 从绘本展示页跳转到新的绘本展示页
  // 用于大重画
  // 需要额外传递绘本Id
  static void goToPicNew(BuildContext context, String storyId, bool forceLandscape, bool fromPicBook) {
    print('_____________________大重画 跳转');
    print("______________传递的formPicBook: {$fromPicBook}");
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => PicBook(storyId: storyId, forceLandscape: forceLandscape, fromPicBook: fromPicBook),
      ),
    );
  }

  // 用于从历史绘本界面跳转到横屏展示绘本
  static void goToPicShow(BuildContext context, String storyId) {
    print('_____________________历史绘本展示 跳转');
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PicBookShow(storyId: storyId),
      ),
    );
  }
}