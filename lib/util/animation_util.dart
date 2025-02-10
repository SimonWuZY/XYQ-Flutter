import 'package:flutter/material.dart';

class AnimationUtil {
  static Animation<Color?> createColorAnimation(AnimationController controller) {
    return TweenSequence<Color?>([
      TweenSequenceItem(
        weight: 1.0,
        tween: ColorTween(begin: Colors.redAccent, end: Colors.yellowAccent),
      ),
      TweenSequenceItem(
        weight: 1.0,
        tween: ColorTween(begin: Colors.yellowAccent, end: Colors.blueAccent),
      ),
      TweenSequenceItem(
        weight: 1.0,
        tween: ColorTween(begin: Colors.blueAccent, end: Colors.purpleAccent),
      ),
      TweenSequenceItem(
        weight: 1.0,
        tween: ColorTween(begin: Colors.purpleAccent, end: Colors.redAccent),
      ),
    ]).animate(controller);
  }
}
