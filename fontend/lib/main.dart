import 'package:aigc_/dao/login_dao.dart';
import 'package:aigc_/navigator/tab_navigator.dart';
import 'package:aigc_/pages/login_page.dart';
import 'package:aigc_/widget/loading_widget.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hi_cache/flutter_hi_cache.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: FutureBuilder<dynamic>(
        future: HiCache.preInit().then((_) => Future.delayed(const Duration(seconds: 1))),
        builder: (BuildContext context, AsyncSnapshot<dynamic> snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            if (LoginDao.getBoardingPass() == null) {
              print('____________Navigating to LoginPage');
              return const LoginPage();
            } else {
              print('________Navigating to TabNavigator');
              return const TabNavigator();
            }
          } else {
            print('___________________Showing CircularProgressIndicator');
            return const LoadingScreen();
          }
        },
      ),
    );
  }
}
