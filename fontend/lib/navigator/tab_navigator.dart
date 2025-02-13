import 'package:aigc_/widget/over_lay_screen.dart';
import 'package:logger/logger.dart';
import 'package:aigc_/pages/history_pic.dart';
import 'package:aigc_/pages/display_draw.dart';
import 'package:aigc_/pages/personal.dart';
import 'package:flutter/material.dart';
import 'package:curved_navigation_bar/curved_navigation_bar.dart';
import 'package:aigc_/util/animation_util.dart';


class TabNavigator extends StatefulWidget {
  const TabNavigator({super.key});

  @override
  State<TabNavigator> createState() => _TabNavigatorState();
}

class _TabNavigatorState extends State<TabNavigator> with SingleTickerProviderStateMixin {
  final logger = Logger();
  int _currentIndex = 1;
  final PageController _controller = PageController(initialPage: 1);
  bool _isOverlayVisible = false;
  late AnimationController _animationController;
  late Animation<Color?> _colorAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 6),
    )..repeat();

    _colorAnimation = AnimationUtil.createColorAnimation(_animationController);
  }

  void _showOverlay() {
    setState(() {
      _isOverlayVisible = true;
    });
  }

  void _hideOverlay() {
    setState(() {
      _isOverlayVisible = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    logger.i("Tabbar success! $_currentIndex");
    print('Current Index: $_currentIndex');
    return Scaffold(
      body: Stack(
        children: [
          PageView(
            controller: _controller,
            physics: const NeverScrollableScrollPhysics(),
            onPageChanged: (index) {
              setState(() {
                _currentIndex = index;
              });
            },
            children: [
              HistoryPic(),
              DisplayDraw(
                showOverlay: _showOverlay,
                hideOverlay: _hideOverlay,
                isOverlayVisible: _isOverlayVisible,
                colorAnimation: _colorAnimation,
              ),
              Personal(),
            ],
          ),
          if (_isOverlayVisible && _currentIndex == 1) // Only show overlay on DisplayDraw page
            OverlayScreen(
              hideOverlay: _hideOverlay,
              colorAnimation: _colorAnimation,
            ),
        ],
      ),
      bottomNavigationBar: CurvedNavigationBar(
        index: _currentIndex,
        backgroundColor: Colors.transparent,
        color: const Color.fromARGB(255, 254, 246, 183),
        items: const <Widget>[
          Icon(Icons.list, size: 30),
          Icon(Icons.add, size: 30),
          Icon(Icons.compare_arrows, size: 30),
        ],
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
          _controller.jumpToPage(index);
        },
      ),
    );
  }
}
