import 'dart:developer';
import 'package:aigc_/dao/http_utils.dart';
import 'package:aigc_/util/navigator_util.dart';
import 'package:aigc_/util/util.dart';
import 'package:flutter/material.dart';
import 'package:logger/logger.dart';
import 'package:gap/gap.dart';
import 'package:avatar_glow/avatar_glow.dart';

class DisplayDraw extends StatefulWidget {
  DisplayDraw({
    super.key,
    required this.showOverlay,
    required this.hideOverlay,
    required this.isOverlayVisible,
    required this.colorAnimation,
  });

  final VoidCallback showOverlay;
  final VoidCallback hideOverlay;
  final bool isOverlayVisible;
  final Animation<Color?> colorAnimation;

  @override
  State<DisplayDraw> createState() => _DisplayDrawState();
}

class _DisplayDrawState extends State<DisplayDraw>
    with SingleTickerProviderStateMixin {
  bool creatStatus = false;
  final inputController = TextEditingController();
  bool _isListening = false;
  late STTUtil _sttUtil;
  bool _status = false;

  Logger logger = Logger();
  String? storyId;
  String? historyText;
  bool _isDisposed = false;

  @override
  void initState() {
    super.initState();
    _sttUtil = STTUtil();
  }

  @override
  void dispose() {
    inputController.dispose();
    _sttUtil.dispose();
    _isDisposed = true; // 设置 disposed 标志
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // 解决键盘弹起影响页面问题
      resizeToAvoidBottomInset: false,
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          WillPopScope(
            onWillPop: () async {
              if (widget.isOverlayVisible) {
                // Do not pop the page if overlay is visible
                return false;
              }
              return true;
            },
            child: Padding(
              padding: const EdgeInsets.all(15),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: <Widget>[
                  const Text(
                    '星语桥',
                    style: TextStyle(fontSize: 70, fontFamily: "Heiti"),
                  ),
                  const Text(
                    '用绘本连接星星与爱',
                    style: TextStyle(
                        fontSize: 18,
                        color: Colors.black87,
                        fontFamily: "pomo"),
                  ),
                  const SizedBox(height: 10),
                  Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(30),
                      gradient: const LinearGradient(
                        colors: [
                          Color.fromARGB(214, 244, 89, 54),
                          Color.fromARGB(255, 141, 59, 255)
                        ],
                      ),
                    ),
                    padding: const EdgeInsets.all(3), // 添加内边距以显示边框
                    child: TextField(
                      controller: inputController,
                      maxLines: null,
                      decoration: InputDecoration(
                        hintText: '创作一部爱冒险的小男孩的故事',
                        hintMaxLines: 2, // 设置提示文字的最大行数
                        fillColor: Colors.white,
                        filled: true,
                        border: OutlineInputBorder(
                          borderRadius:
                              BorderRadius.circular(27), // 确保边框半径比外层容器小
                          borderSide: BorderSide.none,
                        ),
                        contentPadding: const EdgeInsets.symmetric(
                            vertical: 10, horizontal: 15),
                        suffixIcon: Padding(
                          padding: const EdgeInsets.only(right: 0), // 调整按钮的右边距
                          child: Wrap(
                            spacing: -20, // 调整两个按钮之间的间距
                            alignment: WrapAlignment.end,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.arrow_forward,
                                    color: Color.fromARGB(255, 255, 82, 137)),
                                onPressed: () {
                                  if (!_status ||
                                      (historyText != inputController.text)) {
                                    logger.i("保存的文本:$historyText");
                                    _send_outline();
                                  } else {
                                    logger.i("跳转保存的文本:$historyText");
                                    // 跳转到绘本展示页面
                                    pic_show(context);
                                  }
                                  _getInput_navigator(context);
                                },
                              ),
                              AvatarGlow(
                                glowRadiusFactor: 75.0,
                                animate: _isListening,
                                glowColor: Theme.of(context).primaryColor,
                                child: RawMaterialButton(
                                  onPressed: _listen,
                                  shape: const CircleBorder(),
                                  padding: const EdgeInsets.all(8.0),
                                  child: Icon(
                                    _isListening ? Icons.mic : Icons.mic_none,
                                    color:
                                        const Color.fromARGB(255, 255, 82, 137),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                      style: TextStyle(
                        fontFamily: 'pomo', // 设置自定义字体
                        fontSize: 15,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (widget.isOverlayVisible) _buildOverlay(),
        ],
      ),
    );
  }

  Widget _buildOverlay() {
    return IgnorePointer(
      ignoring: false, // Allow interaction with the overlay
      child: Stack(
        children: [
          Positioned.fill(
            child: Material(
              color: Colors.black54,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    AnimatedBuilder(
                      animation: widget.colorAnimation,
                      builder: (context, child) {
                        return CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation<Color?>(
                              widget.colorAnimation.value),
                        );
                      },
                    ),
                    const Gap(16),
                    const Text(
                      "绘本正在制作...大约需要一分钟时间",
                      style: TextStyle(
                          fontSize: 18,
                          color: Colors.white,
                          fontFamily: 'Heiti'),
                    ),
                    const Gap(5),
                    const Text(
                      "去其他页面看看吧",
                      style: TextStyle(
                          fontSize: 18,
                          color: Colors.white,
                          fontFamily: 'Heiti'),
                    ),
                    const Gap(16),
                    TextButton(
                      child: const Text(
                        "终止",
                        style: TextStyle(
                            fontSize: 18,
                            color: Colors.white54,
                            fontFamily: 'Heiti'),
                      ),
                      onPressed: widget.hideOverlay,
                    ),
                  ],
                ),
              ),
            ),
          ),
          Positioned(
            right: 16.0,
            top: 16.0,
            child: IconButton(
              icon: const Icon(Icons.close, color: Colors.white),
              onPressed: widget.hideOverlay,
            ),
          ),
        ],
      ),
    );
  }

  void _getInput_navigator(BuildContext context) async {
    print("成功获取：${inputController.text}");
    log("成功获取：${inputController.text}");

    historyText = inputController.text;
    logger.i("保存的文本:$historyText");
  }

  void _send_outline() async {
    widget.showOverlay();
    var result = await set_outline(inputController.text);
    widget.hideOverlay();
    if (_isDisposed) return; // 检查 disposed 标志
    if (result != null) {
      setState(() {
        historyText = inputController.text;
        // 获取绘本Id
        storyId = result['storyId'];
        logger.i("绘本生成成功 storyId:$storyId");
        _status = true;
      });
      // 显示成功弹窗
      showResultDialog1(context, true);
    } else {
      logger.e("绘本生成错误！");
      storyId = null;
      // 显示失败弹窗
      showResultDialog1(context, false);
    }
  }

  void _listen() async {
    if (!_isListening) {
      log("麦克风初始化________！");
      bool available = await _sttUtil.initialize();
      log("麦克风初始化完成！");
      log("麦克风状态$available");

      if (available) {
        setState(() {
          _isListening = true;
        });

        _sttUtil.startListening((res) {
          setState(() {
            inputController.text += res;
            log('监听到的文字：$res');
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

  void showResultDialog1(BuildContext context, bool isSuccess) {
    showDialog(
      context: context,
      barrierDismissible: false, // 设置为false，用户不能通过点击对话框外部区域来关闭对话框
      builder: (BuildContext context) {
        return AlertDialog(
          backgroundColor: isSuccess ? Colors.green[100] : Colors.red[100],
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
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
                if (isSuccess) {
                  pic_show(context);
                }
              },
            ),
          ],
        );
      },
    );
  }

  void pic_show(BuildContext context) {
    if (storyId != null) {
      NavigatorUtil.goToPic(context, storyId!, true);
    } else {
      logger.e("绘本ID未找到！");
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: const Row(
              children: [
                Icon(Icons.error, color: Colors.red),
                SizedBox(width: 8),
                Text(
                  "错误",
                  style: TextStyle(fontFamily: 'pomo', fontSize: 18),
                ),
              ],
            ),
            content: const Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  "当前创作绘本为空",
                  style: TextStyle(fontFamily: 'pomo', fontSize: 16),
                ),
                SizedBox(height: 8),
                Text(
                  "请重新输入大纲",
                  style: TextStyle(fontFamily: 'pomo', fontSize: 16),
                ),
              ],
            ),
            actions: <Widget>[
              TextButton(
                child: Text(
                  "取消",
                  style: TextStyle(fontFamily: 'pomo', fontSize: 16),
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
  }
}
