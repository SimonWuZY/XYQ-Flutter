import 'package:aigc_/dao/http_utils.dart';
import 'package:aigc_/util/story_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:logger/logger.dart';

class PicBookShow extends StatefulWidget {
  final String storyId;

  const PicBookShow({Key? key, required this.storyId}) : super(key: key);

  @override
  _PicBookState createState() => _PicBookState();
}

class _PicBookState extends State<PicBookShow>
    with SingleTickerProviderStateMixin {
  Logger logger = Logger();
  List<StoryPage> _pages = [];
  PageController _pageController = PageController();

  @override
  void initState() {
    super.initState();
    // 强制横屏
    logger.i("强制横屏");
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeRight,
      DeviceOrientation.landscapeLeft,
    ]);

    logger.i("_____获取绘本函数");
    _fetchStoryData();
  }

  @override
  void dispose() {
    // 恢复竖屏
    logger.i("强制竖屏");
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.portraitUp,
      DeviceOrientation.portraitDown,
    ]);
    // _pageController.dispose();
    super.dispose();
  }

  Future<void> _fetchStoryData() async {
    List<StoryPage>? pages = await getPics(widget.storyId);
    logger.i("绘本图片：$pages");
    if (pages != null) {
      setState(() {
        _pages = pages;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      extendBodyBehindAppBar: true, // 扩展主体到AppBar后面
      resizeToAvoidBottomInset: false, // 添加这一行
      appBar: AppBar(
        backgroundColor: Colors.transparent, // 设置透明背景
        elevation: 0, // 去掉阴影
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_outlined,
              color: Colors.white),
          onPressed: () {
            Navigator.of(context).pop();
          },
        ),
      ),
      body: _pages.isEmpty
          ? Center(child: CircularProgressIndicator())
          : LayoutBuilder(
              builder: (BuildContext context, BoxConstraints constraints) {
                return Padding(
                  padding: const EdgeInsets.only(top: 0), // 调整整体下移的距离
                  child: Stack(
                    children: [
                      // 黑色蒙版
                      Positioned.fill(
                        child: Container(
                          color: Colors.black.withOpacity(0.4), // 半透明黑色背景
                        ),
                      ),
                      PageView.builder(
                        controller: _pageController,
                        itemCount: _pages.length,
                        itemBuilder: (context, index) {
                          return _buildPage(
                              _pages[index], constraints.maxWidth);
                        },
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }

  Widget _buildPage(StoryPage page, double maxWidth) {
    return Center(
      child: LayoutBuilder(
        builder: (BuildContext context, BoxConstraints constraints) {
          return Stack(
            children: [
              AspectRatio(
                aspectRatio: 16 / 9,
                child: FittedBox(
                  fit: BoxFit.cover,
                  child: Image.network(page.imageUri),
                ),
              ),
              Positioned(
                bottom: 0,
                left: 0,
                right: 0,
                child: Container(
                  width: constraints.maxWidth,
                  color: Colors.black.withOpacity(0.6), // 半透明背景
                  padding: const EdgeInsets.all(10),
                  child: SingleChildScrollView(
                    child: Text(
                      page.text, // 文本框内容
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontFamily: 'pomo', // 设置字体
                      ),
                    ),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
