import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:logger/logger.dart';
import 'package:aigc_/util/navigator_util.dart';
import 'package:aigc_/dao/login_dao.dart';
import 'package:aigc_/dao/user_dao.dart';
import 'dart:io';

class Personal extends StatefulWidget {
  const Personal({super.key});

  @override
  State<Personal> createState() => _PersonalState();
}

class _PersonalState extends State<Personal> with AutomaticKeepAliveClientMixin {
  final logger = Logger();
  File? _image;
  final picker = ImagePicker();
  String _nickname = "您的昵称";
  bool _isEditingNickname = false;
  final TextEditingController _nicknameController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _fetchUserData();
  }

  Future<void> _fetchUserData() async {
    try {
      String token = await LoginDao.getBoardingPass();
      var userInfo = await UserDao.getUserInfo(token: token);
      setState(() {
        _nickname = userInfo['nickname'] ?? _nickname;
        _nicknameController.text = _nickname;
        if (userInfo['avatar'] != null) {
          _image = File(userInfo['avatar']!);
        }
      });
      logger.i("Fetched user data: ${userInfo.toString()}");
    } catch (e) {
      logger.e("Error fetching user data: $e");
    }
  }

  Future<void> _pickImage() async {
    try {
      final pickedFile = await picker.pickImage(source: ImageSource.gallery);
      if (pickedFile != null) {
        setState(() {
          _image = File(pickedFile.path);
        });
        _uploadUserData();
        logger.i("Image picked: ${pickedFile.path}");
      } else {
        logger.w("No image selected.");
      }
    } catch (e) {
      logger.e("Error picking image: $e");
    }
  }

  void _toggleNicknameEditing() {
    setState(() {
      _isEditingNickname = !_isEditingNickname;
      if (!_isEditingNickname) {
        _nickname = _nicknameController.text;
        _uploadUserData();
        logger.i("Nickname changed to: $_nickname");
      }
    });
  }

  Future<void> _uploadUserData() async {
    try {
      String token = await LoginDao.getBoardingPass();
      bool success = await UserDao.updateUserInfo(
        token: token,
        avatarPath: _image?.path,
        nickname: _nickname,
      );
      if (success) {
        logger.i("User data uploaded successfully.");
      } else {
        logger.w("Failed to upload user data.");
      }
    } catch (e) {
      logger.e("Error uploading user data: $e");
    }
  }

  Future<void> _logout() async {
    try {
      logger.i("User confirmed logout.");
      LoginDao.logout();
      logger.i("User logged out.");
    } catch (e) {
      logger.e("Logout error: $e");
    }
  }

  @override
  bool get wantKeepAlive => true;

  @override
  Widget build(BuildContext context) {
    super.build(context);
    NavigatorUtil.updateContext(context);
    return Scaffold(
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          child: Column(
            children: <Widget>[
              const SizedBox(height: 100),
              GestureDetector(
                onTap: _pickImage,
                child: CircleAvatar(
                  radius: 50,
                  backgroundColor: Colors.grey[300],
                  backgroundImage: _image != null ? FileImage(_image!) : null,
                  child: _image == null
                      ? const Text(
                          '您',
                          style: TextStyle(fontSize: 40, color: Colors.white),
                        )
                      : null,
                ),
              ),
              const SizedBox(height: 10),
              GestureDetector(
                onTap: _toggleNicknameEditing,
                child: _isEditingNickname
                    ? TextField(
                        controller: _nicknameController,
                        decoration: const InputDecoration(hintText: "输入新的昵称"),
                        onSubmitted: (value) => _toggleNicknameEditing(),
                      )
                    : Text(
                        _nickname,
                        style: const TextStyle(fontSize: 24),
                      ),
              ),
              const Divider(),
              ListTile(
                leading: const Icon(Icons.lock_outline, color: Colors.green),
                title: const Text('账号与安全'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  logger.i("Navigating to Account and Security.");
                  // 账号安全 修改密码
                },
              ),
              ListTile(
                leading: const Icon(Icons.people, color: Colors.orange),
                title: const Text('朋友圈'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  logger.i("Navigating to Friends Circle.");
                  // 朋友圈跳转
                },
              ),
              ListTile(
                leading: const Icon(Icons.insert_drive_file, color: Colors.green),
                title: const Text('文件'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  logger.i("Navigating to Files.");
                  // 文件跳转
                },
              ),
              ListTile(
                leading: const Icon(Icons.star_border, color: Colors.blue),
                title: const Text('收藏'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  logger.i("Navigating to Favorites.");
                  // 收藏跳转
                },
              ),
              ListTile(
                leading: const Icon(Icons.palette, color: Colors.green),
                title: const Text('主题'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  logger.i("Navigating to Themes.");
                  // 主题跳转
                },
              ),
              ListTile(
                leading: const Icon(Icons.settings, color: Colors.blue),
                title: const Text('设置'),
                trailing: const Icon(Icons.arrow_forward_ios),
                onTap: () {
                  logger.i("Opening Settings.");
                  // 这里可以加入设置的其他操作
                },
              ),
              const Divider(),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _logout,
                    child: const Text('退出登录'),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
