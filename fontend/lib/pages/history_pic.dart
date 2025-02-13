import 'package:aigc_/dao/http_utils.dart';
import 'package:aigc_/util/navigator_util.dart';
import 'package:aigc_/util/story_page.dart';
import 'package:aigc_/widget/result_dialog.dart';
import 'package:flutter/material.dart';
import 'package:logger/logger.dart';

class HistoryPic extends StatefulWidget {
  final double pageViewHeightFraction;
  final double pageViewWidthFraction;
  final double scaleFraction;

  HistoryPic({
    this.pageViewHeightFraction = 0.6,
    this.pageViewWidthFraction = 0.8,
    this.scaleFraction = 0.8,
  });

  @override
  _HistoryPicState createState() => _HistoryPicState();
}

class _HistoryPicState extends State<HistoryPic> {
  List<StoryPageId> _data = [];
  Logger logger = Logger();
  PageController _pageController;
  int _currentPageIndex = 0;
  bool _showButtons = false; // 用于控制按钮显示状态

  _HistoryPicState() : _pageController = PageController(viewportFraction: 0.8);

  @override
  void initState() {
    super.initState();
    _fetchData();
  }

  Future<void> _fetchData() async {
    logger.i("___开始获取历史绘本的封面和标题");
    List<StoryPageId>? fetchedData = await get_all_story();
    if (fetchedData != null && fetchedData.isNotEmpty) {
      setState(() {
        logger.i("开始构造页面");
        print("当前： $fetchedData");
        _data = fetchedData;
        print("当前页面： $_data");
      });
    } else {
      // 处理数据获取失败的情况
      print("Failed to fetch data");
      showResultDialogHis(context, false);
    }
  }

  @override
  Widget build(BuildContext context) {
    double pageViewHeight =
        MediaQuery.of(context).size.height * widget.pageViewHeightFraction;
    double pageViewWidth =
        MediaQuery.of(context).size.width * widget.pageViewWidthFraction;
    double progressBarHeight = MediaQuery.of(context).size.height * 0.6;

    return Scaffold(
      body: Stack(
        children: [
          Center(
            child: _data.isEmpty
                ? CircularProgressIndicator()
                : Stack(
                    children: [
                      Positioned(
                        left: MediaQuery.of(context).size.width * 0.1, // 左移
                        top: (MediaQuery.of(context).size.height -
                                pageViewHeight) /
                            2, // 垂直居中
                        child: Container(
                          height: pageViewHeight,
                          width: pageViewWidth,
                          child: PageView.builder(
                            controller: _pageController,
                            scrollDirection: Axis.vertical, // 设置为垂直方向滑动
                            physics: BouncingScrollPhysics(), // 添加惯性效果
                            itemCount: _data.length,
                            onPageChanged: (index) {
                              setState(() {
                                _currentPageIndex = index;
                              });
                            },
                            itemBuilder: (context, index) {
                              return GestureDetector(
                                onTap: () {
                                  logger.i("开始跳转展示绘本");
                                  var storyId = _data[index].storyId;
                                  logger.i("Story ID: $storyId");
                                  try {
                                    NavigatorUtil.goToPicShow(context, storyId);
                                    logger.i("导航成功");
                                  } catch (e) {
                                    logger.e("导航失败: $e");
                                  }
                                },
                                onLongPress: () {
                                  setState(() {
                                    _showButtons = true; // 显示按钮
                                  });
                                },
                                child: AnimatedBuilder(
                                  animation: _pageController,
                                  builder: (context, child) {
                                    double value = 1.0;
                                    if (_pageController
                                        .position.haveDimensions) {
                                      value = _pageController.page! - index;
                                      value = (1 -
                                              (value.abs() *
                                                  widget.scaleFraction))
                                          .clamp(0.0, 1.0);
                                    }
                                    return Center(
                                      child: Transform.scale(
                                        scale: Curves.easeOut.transform(value),
                                        child: Padding(
                                          padding: const EdgeInsets.symmetric(
                                              vertical: 10.0), // 调整上下间距
                                          child: child,
                                        ),
                                      ),
                                    );
                                  },
                                  child: Card(
                                    child: Column(
                                      children: [
                                        Expanded(
                                          child: Image.network(
                                            _data[index].imageUri,
                                            fit: BoxFit.cover,
                                          ),
                                        ),
                                        Padding(
                                          padding: const EdgeInsets.all(8.0),
                                          child: Text(
                                            _data[index].text,
                                            style: TextStyle(fontSize: 20),
                                          ),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                      Positioned(
                        right: 20, // 右侧位置
                        top: (MediaQuery.of(context).size.height -
                                progressBarHeight) /
                            2, // 垂直居中
                        child: Container(
                          height: progressBarHeight,
                          width: 10,
                          decoration: BoxDecoration(
                            color: Colors.grey[300],
                            borderRadius: BorderRadius.circular(5),
                          ),
                          child: LayoutBuilder(
                            builder: (context, constraints) {
                              double indicatorHeight = 20.0; // 小色块高度
                              return AnimatedBuilder(
                                animation: _pageController,
                                builder: (context, child) {
                                  double position = 0.0;
                                  if (_pageController.hasClients) {
                                    double pagePosition = _pageController
                                            .page ??
                                        _pageController.initialPage.toDouble();
                                    position =
                                        (pagePosition / (_data.length - 1)) *
                                            (constraints.maxHeight -
                                                indicatorHeight);
                                  }
                                  return Stack(
                                    alignment: Alignment.topCenter,
                                    children: [
                                      Positioned(
                                        top: position,
                                        child: Container(
                                          height: indicatorHeight,
                                          width: 10,
                                          decoration: BoxDecoration(
                                            color: Colors.orange,
                                            borderRadius:
                                                BorderRadius.circular(5),
                                          ),
                                        ),
                                      ),
                                    ],
                                  );
                                },
                              );
                            },
                          ),
                        ),
                      ),
                    ],
                  ),
          ),
          Positioned(
            top: 100, // 调整标题的垂直位置
            left: 0,
            right: 0,
            child: Center(
              child: ShaderMask(
                shaderCallback: (bounds) => const LinearGradient(
                  colors: [Colors.orange, Colors.red],
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                ).createShader(bounds),
                child: const Text(
                  '绘本展示区',
                  style: TextStyle(
                    fontFamily: 'Guazi', // 使用自定义字体
                    fontSize: 65,
                    fontWeight: FontWeight.bold,
                    color: Colors.white, // 必须设置颜色，否则渐变无效
                  ),
                ),
              ),
            ),
          ),
          if (_showButtons)
            ModalBarrier(
              color: Colors.black.withOpacity(0.5),
              dismissible: false,
            ),
          if (_showButtons)
            Positioned(
              bottom: 30,
              left: MediaQuery.of(context).size.width * 0.3,
              right: MediaQuery.of(context).size.width * 0.3,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  FloatingActionButton(
                    heroTag: "delete",
                    onPressed: () {
                      setState(() async {
                        bool? result = await delete_story(
                            _data[_currentPageIndex].storyId);
                        if (result != null) {
                          if (result) {
                            _data.removeAt(_currentPageIndex);
                            showDialog(
                              context: context,
                              builder: (BuildContext context) {
                                return AlertDialog(
                                  title: Text("删除成功！"),
                                  actions: [
                                    TextButton(
                                      onPressed: () =>
                                          Navigator.of(context).pop(),
                                      child: const Text("确定"),
                                    ),
                                  ],
                                );
                              },
                            );
                          } else {
                            showDialog(
                              context: context,
                              builder: (BuildContext context) {
                                return AlertDialog(
                                  title: Text("删除异常"),
                                  actions: [
                                    TextButton(
                                      onPressed: () =>
                                          Navigator.of(context).pop(),
                                      child: const Text("确定"),
                                    ),
                                  ],
                                );
                              },
                            );
                          }
                        } else {
                          showDialog(
                            context: context,
                            builder: (BuildContext context) {
                              return AlertDialog(
                                title: Text("网络异常"),
                                actions: [
                                  TextButton(
                                    onPressed: () =>
                                        Navigator.of(context).pop(),
                                    child: const Text("确定"),
                                  ),
                                ],
                              );
                            },
                          );
                        }
                        _showButtons = false; // 隐藏按钮
                      });
                    },
                    child: Icon(Icons.delete),
                  ),
                  FloatingActionButton(
                    heroTag: "hide",
                    onPressed: () {
                      setState(() {
                        _showButtons = false; // 隐藏按钮
                      });
                    },
                    child: Icon(Icons.arrow_back),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
