import 'package:flutter/material.dart';
import 'package:gap/gap.dart';

class OverlayScreen extends StatelessWidget {
  final VoidCallback hideOverlay;
  final Animation<Color?> colorAnimation;

  const OverlayScreen({super.key, required this.hideOverlay, required this.colorAnimation});

  @override
  Widget build(BuildContext context) {
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
                      animation: colorAnimation,
                      builder: (context, child) {
                        return CircularProgressIndicator(
                          valueColor: AlwaysStoppedAnimation<Color?>(colorAnimation.value),
                        );
                      },
                    ),
                    const Gap(16),
                    const Text(
                      "绘本正在制作...大约需要一分钟时间",
                      style: TextStyle(fontSize: 18, color: Colors.white, fontFamily: 'Heiti'),
                    ),
                    const Gap(5),
                    const Text(
                      "去其他页面看看吧",
                      style: TextStyle(fontSize: 18, color: Colors.white, fontFamily: 'Heiti'),
                    ),
                    const Gap(16),
                    TextButton(
                      child: const Text(
                        "终止",
                        style: TextStyle(fontSize: 18, color: Colors.white54, fontFamily: 'Heiti'),
                      ),
                      onPressed: hideOverlay,
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
              onPressed: hideOverlay,
            ),
          ),
        ],
      ),
    );
  }
}
