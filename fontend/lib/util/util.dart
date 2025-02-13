import 'dart:developer';

import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:highlight_text/highlight_text.dart';
import 'package:flutter/material.dart';

// 基于单例模式实现的工具类
class TTSUtil {
  TTSUtil._();

  static final TTSUtil _manager = TTSUtil._();

  factory TTSUtil() {
    return _manager;
  }

  late FlutterTts flutterTts;

  void initTTS() {
    flutterTts = FlutterTts();
  }

  Future<void> speak(String text) async {
    // 设置语言
    await flutterTts.setLanguage("zh-CN");

    // 设置音量
    await flutterTts.setVolume(0.8);

    // 设置语速
    await flutterTts.setSpeechRate(0.3);

    // 音调
    await flutterTts.setPitch(1.0);

    if (text.isNotEmpty) {
      log('需要转换的文本：$text');
      await flutterTts.speak(text);
    }
  }

  /// 暂停
  Future<void> pause() async {
    await flutterTts.pause();
  }

  /// 结束
  Future<void> stop() async {
    await flutterTts.stop();
  }
}

// STT工具类 单例模式
class STTUtil {
  STTUtil._();

  static final STTUtil _manager = STTUtil._();

  factory STTUtil(){
    return _manager;
  }

  late SpeechToText _speechToText;

  /// 初始化语音识别。
  Future<bool> initialize() async {
    _speechToText = SpeechToText();
    return await _speechToText.initialize(
      onStatus: (status) {
        log('onStatus: $status');
      },
      onError: (error) {
        log('onError:$error');
      },
    );
  }

  /// 开始语音识别。
  Future<void> startListening(Function(String) onResult) async {
    if (_speechToText.isNotListening) {
      await _speechToText.listen(
        onResult: (result) {
          log('监听到的内容:$result');
          onResult(result.recognizedWords);
        },
          // 监听的语言
          localeId: "zh_CN"
      );
    }
  }

  /// 停止语音识别。
  Future<void> stopListening() async {
    if (_speechToText.isListening) {
      await _speechToText.stop();
    }
  }

  /// 获取语音识别的状态。
  SpeechToTextState getState() {
    return _speechToText.isListening
        ? SpeechToTextState.listening
        : SpeechToTextState.notListening;
  }

  /// 释放资源。
  void dispose() {
    _speechToText.cancel();
  }
}

enum SpeechToTextState {
  listening,
  notListening,
}

// 单词高亮显示 可自己构建一个需要高亮显示的字典树 这个与TTS和STT无关
final Map<String, HighlightedWord> highlights = {
  'flutter': HighlightedWord(
    onTap: () => print('flutter'),
    textStyle: const TextStyle(
      color: Colors.blue,
      fontWeight: FontWeight.bold,
    ),
  ),
  'voice': HighlightedWord(
    onTap: () => print('voice'),
    textStyle: const TextStyle(
      color: Colors.green,
      fontWeight: FontWeight.bold,
    ),
  ),
  'subscribe': HighlightedWord(
    onTap: () => print('subscribe'),
    textStyle: const TextStyle(
      color: Colors.red,
      fontWeight: FontWeight.bold,
    ),
  ),
  'like': HighlightedWord(
    onTap: () => print('like'),
    textStyle: const TextStyle(
      color: Colors.blueAccent,
      fontWeight: FontWeight.bold,
    ),
  ),
  'comment': HighlightedWord(
    onTap: () => print('comment'),
    textStyle: const TextStyle(
      color: Colors.green,
      fontWeight: FontWeight.bold,
    ),
  ),
};

// 验证用户名的正则表达式
bool isValidUserName(String userName) {
  final RegExp userNameRegExp = RegExp(r'^[a-zA-Z0-9]{6,20}$'); // 6-20位的字母或数字
  return userNameRegExp.hasMatch(userName);
}

  // 验证密码的正则表达式
  bool isValidPassword(String password) {
    final RegExp passWordRegExp = RegExp(r'^[a-zA-Z0-9@#$%^&*]{8,20}$'); // 8-20位的字母、数字或特殊字符
    return passWordRegExp.hasMatch(password);
  }