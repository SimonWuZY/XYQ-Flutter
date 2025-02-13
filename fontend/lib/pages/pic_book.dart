import 'package:aigc_/dao/http_utils.dart';
import 'package:aigc_/util/navigator_util.dart';
import 'package:aigc_/util/story_page.dart';
import 'package:aigc_/util/util.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:gap/gap.dart';
import 'package:logger/logger.dart';

class PicBook extends StatefulWidget {
  final String storyId;
  final bool forceLandscape; // 添加这个参数
  final bool fromPicBook; // 添加这个参数

  const PicBook(
      {Key? key,
      required this.storyId,
      this.forceLandscape = false,
      this.fromPicBook = false})
      : super(key: key);

  @override
  _PicBookState createState() => _PicBookState();
}

class _PicBookState extends State<PicBook> with SingleTickerProviderStateMixin {
  bool _isToolbarVisible = false;
  bool _isSecondButtonToggled = false; // 第二个按钮的状态
  bool _isMicButtonVisible = false; // 麦克风按钮的状态
  Logger logger = Logger();
  List<StoryPage> _pages = [];
  PageController _pageController = PageController();
  TextEditingController _editingController = TextEditingController();
  AnimationController? _animationController;
  Animation<Offset>? _animation;
  bool _shouldRestorePortrait = true; // 是否需要恢复竖屏
  bool _isListening = false;
  late STTUtil _sttUtil;

  @override
  void initState() {
    logger.i("构造页面当前的 fromPicBook: ${widget.fromPicBook}");
    super.initState();
    _setOrientation();

    logger.i("_____获取绘本函数");
    _fetchStoryData();

    _sttUtil = STTUtil(); // 初始化 _sttUtil
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );

    _animation = Tween<Offset>(
      begin: Offset(0, 1),
      end: Offset(0, 0),
    ).animate(CurvedAnimation(
      parent: _animationController!,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _resetOrientation();
    _pageController.dispose();
    _animationController?.dispose();
    super.dispose();
  }

  void _setOrientation() {
    if (widget.forceLandscape) {
      logger.i("强制横屏");
      SystemChrome.setPreferredOrientations([
        DeviceOrientation.landscapeRight,
        DeviceOrientation.landscapeLeft,
      ]);
    }
  }

  void _resetOrientation() {
    logger.i("此时的fromPicBook: ${widget.fromPicBook}");
    if (widget.forceLandscape &&
        _shouldRestorePortrait) {
      logger.i("强制竖屏");
      SystemChrome.setPreferredOrientations([
        DeviceOrientation.portraitUp,
        DeviceOrientation.portraitDown,
      ]);
    }
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

  void _toggleToolbar() {
    setState(() {
      _isToolbarVisible = !_isToolbarVisible;
    });
  }

  void _toggleSecondButton() {
    logger.i("____调用1");
    setState(() {
      logger.i("____调用2");
      _isSecondButtonToggled = !_isSecondButtonToggled;
      _isMicButtonVisible = !_isMicButtonVisible; // 切换麦克风按钮的状态
      if (_isSecondButtonToggled) {
        logger.i("____调用3");
        _animationController?.forward();
      } else {
        logger.i("____调用4");
        _animationController?.reverse();
      }
    });
  }

  Future<void> _updateCurrentPage(String storyId, int currentPage) async {
    logger.i("重画页数 = $currentPage");
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return const AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 10),
              Text(
                "当前页重画中请耐心等待....",
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 20,
                  fontFamily: 'pomo', // 设置字体
                ),
              ),
            ],
          ),
        );
      },
    );

    String? newPageUrl = await update_current(storyId, currentPage.toString());

    if (newPageUrl != null) {
      setState(() {
        logger.i("重画页数{$currentPage}成功");
        Navigator.of(context).pop(); // 关闭等待弹窗
        _pages[currentPage] =
            StoryPage(imageUri: newPageUrl, text: _pages[currentPage].text);
      });
    }
  }

  Future<void> _generateNewStory(String storyId, String requirement) async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return const AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 10),
              Text(
                "绘本重绘中大约一分钟...",
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 20,
                  fontFamily: 'pomo', // 设置字体
                ),
              ),
            ],
          ),
        );
      },
    );

    String? newStoryId = await generate_new_story(storyId, requirement);

    if (newStoryId != null) {
      logger.i("重画后的绘本id = $newStoryId");
      Navigator.of(context).pop(); // 关闭等待弹窗
      // 显示新的带有打勾动画的弹窗
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (BuildContext context) {
          return AlertDialog(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.check_circle,
                  color: Colors.green,
                  size: 60,
                ),
                const Gap(10),
                const Text(
                  "绘本重画完成",
                  style: TextStyle(
                    color: Colors.black54,
                    fontSize: 20,
                    fontFamily: 'pomo', // 设置字体
                  ),
                ),
                const Gap(20),
                ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pop(); // 关闭成功弹窗
                    _shouldRestorePortrait = false; // 跳转到新页面时不恢复竖屏
                    NavigatorUtil.goToPicNew(
                        context, newStoryId, true, true); // 跳转到绘本页面，并强制横屏
                  },
                  child: const Text(
                    "查看绘本",
                    style: TextStyle(
                      color: Colors.black54,
                      fontSize: 20,
                      fontFamily: 'pomo', // 设置字体
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      );
    } else {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (BuildContext context) {
          return AlertDialog(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.error,
                  color: Colors.red,
                  size: 60,
                ),
                const Gap(10),
                const Text(
                  "绘本重画失败",
                  style: TextStyle(
                    color: Colors.black54,
                    fontSize: 20,
                    fontFamily: 'pomo', // 设置字体
                  ),
                ),
                const Gap(20),
                ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).pop(); // 关闭失败弹窗
                    Navigator.of(context).pop(); // 关闭失败弹窗
                  },
                  child: const Text(
                    "返回",
                    style: TextStyle(
                      color: Colors.black54,
                      fontSize: 20,
                      fontFamily: 'pomo', // 设置字体
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      );
    }
  }

  Future<void> _savePage() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return const AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 10),
              Text(
                "正在保存绘本...",
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 16,
                  fontFamily: 'pomo', // 设置字体
                ),
              ),
            ],
          ),
        );
      },
    );

    bool? success = await save_story(widget.storyId);

    Navigator.of(context).pop(); // 关闭等待弹窗

    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (BuildContext context) {
        return AlertDialog(
          content: Row(
            children: [
              Icon(success! ? Icons.check_circle : Icons.error,
                  color: success ? Colors.green : Colors.red),
              SizedBox(width: 10),
              Text(
                success ? "成功保存" : "保存失败",
                style: const TextStyle(
                  color: Colors.black54,
                  fontSize: 20,
                  fontFamily: 'pomo', // 设置字体
                ),
              ),
            ],
          ),
          actions: success
              ? [
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                      Navigator.of(context).pop();
                    },
                    child: const Text("退出绘本预览"),
                  ),
                ]
              : [],
        );
      },
    );
  }

  Future<void> _deletePage() async {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return const AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 10),
              Text(
                "正在删除绘本...",
                style: TextStyle(
                  color: Colors.black54,
                  fontSize: 20,
                  fontFamily: 'pomo', // 设置字体
                ),
              ),
            ],
          ),
        );
      },
    );

    bool? success = await delete_story(widget.storyId);

    Navigator.of(context).pop(); // 关闭等待弹窗

    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (BuildContext context) {
        return AlertDialog(
          content: Row(
            children: [
              Icon(success! ? Icons.check_circle : Icons.error,
                  color: success ? Colors.green : Colors.red),
              SizedBox(width: 10),
              Text(
                success ? "成功删除" : "删除失败",
                style: const TextStyle(
                  color: Colors.black54,
                  fontSize: 16,
                  fontFamily: 'pomo', // 设置字体
                ),
              ),
            ],
          ),
          actions: success
              ? [
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pop();
                      Navigator.of(context).pop();
                    },
                    child: const Text("退出绘本预览"),
                  ),
                ]
              : [],
        );
      },
    );
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
                      Positioned(
                        right: 10,
                        bottom: 10, // 控制按钮下移
                        child: SingleChildScrollView(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              if (_isToolbarVisible) ...[
                                _buildButton(Icons.refresh, () {
                                  int currentPage =
                                      _pageController.page?.toInt() ?? 0;
                                  _updateCurrentPage(
                                      widget.storyId, currentPage);
                                }),
                                const Gap(15),
                                _buildButton(
                                  _isSecondButtonToggled
                                      ? Icons.rotate_left
                                      : Icons.rotate_right,
                                  _toggleSecondButton,
                                ),
                                const Gap(15),
                                _buildButton(Icons.save, _savePage),
                                const Gap(15),
                                _buildButton(Icons.delete, _deletePage),
                                const Gap(15),
                              ],
                              IconButton(
                                onPressed: _toggleToolbar,
                                icon: Icon(_isToolbarVisible
                                    ? Icons.close
                                    : Icons.menu),
                                color: Colors.white,
                                iconSize: 30,
                              ),
                            ],
                          ),
                        ),
                      ),
                      SlideTransition(
                        position: _animation!,
                        child: Align(
                          alignment: Alignment.bottomCenter,
                          child: Container(
                            height: MediaQuery.of(context).size.height *
                                0.3, // 确保文本框占据30%的高度
                            color: Colors.black.withOpacity(0.8),
                            padding: const EdgeInsets.all(10),
                            child: Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: _editingController,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontFamily: 'pomo', // 设置字体
                                    ),
                                    maxLines: 3,
                                    decoration: InputDecoration(
                                      hintText:
                                          '重新绘制整个绘本，请在不改变绘本大纲逻辑上给出需要的修改意见',
                                      hintStyle: const TextStyle(
                                          color: Colors.white54,
                                          fontFamily: 'pomo'), // 设置字体
                                      border: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(10),
                                        borderSide: BorderSide.none,
                                      ),
                                      filled: true,
                                      fillColor: Colors.white.withOpacity(0.2),
                                    ),
                                  ),
                                ),
                                IconButton(
                                  onPressed: () {
                                    _generateNewStory(widget.storyId,
                                        _editingController.text);
                                  },
                                  icon: const Icon(Icons.arrow_forward,
                                      color: Colors.white), // 没有背景的箭头
                                  iconSize: 30,
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      // 麦克风按钮
                      if (_isMicButtonVisible)
                        Positioned(
                          left: 10,
                          bottom: 10,
                          child: RawMaterialButton(
                            onPressed: _listen,
                            shape: const CircleBorder(),
                            padding: const EdgeInsets.all(8.0),
                            child: Icon(
                              _isListening ? Icons.mic : Icons.mic_none,
                              color: const Color.fromARGB(255, 255, 82, 137),
                            ),
                          ),
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

  Widget _buildButton(IconData icon, VoidCallback onPressed) {
    return IconButton(
      onPressed: onPressed,
      icon: Icon(icon),
      color: Colors.white, // 设置按钮颜色为白色
      iconSize: 30,
    );
  }

  void _listen() async {
    if (!_isListening) {
      logger.i("麦克风初始化________！");
      bool available = await _sttUtil.initialize();
      logger.i("麦克风初始化完成！");
      logger.i("麦克风状态$available");

      if (available) {
        setState(() {
          _isListening = true;
        });

        _sttUtil.startListening((res) {
          setState(() {
            _editingController.text += res;
            logger.i('监听到的文字：$res');
          });
        });
      }
    } else {
      setState(() {
        _isListening = false;
      });
      _sttUtil.stopListening();
    }
  }
}
