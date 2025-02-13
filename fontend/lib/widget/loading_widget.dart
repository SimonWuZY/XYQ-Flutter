import 'package:flutter/material.dart';

class LoadingScreen extends StatelessWidget {
  const LoadingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          Image.asset(
            'images/loading1.png', // Ensure the image is in your assets folder and declared in pubspec.yaml
            fit: BoxFit.cover,
          ),
          const Center(
            child: CircularProgressIndicator(),
          ),
        ],
      ),
    );
  }
}