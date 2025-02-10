///保存绘本图片的 url 和 texts 
///用于在PicBook中展示绘本
///@author:Sword
///2024/7/16
class StoryPage {
  final String imageUri;
  final String text;

  StoryPage({required this.imageUri, required this.text});

  factory StoryPage.fromJson(Map<String, dynamic> json) {
    return StoryPage(
      imageUri: json['imageUri'],
      text: json['text'],
    );
  }
}

///保存绘本图片的 url 和 titles 以及 storyId 
///用于在HistoryPic中展示历史绘本的封面和文字
///通过多存的 storyId 实现跳转展示绘本
///@author:Sword
///2024/7/17
class StoryPageId {
  final String imageUri;
  final String text;
  final String storyId;

  StoryPageId({required this.imageUri, required this.text, required this.storyId});

  factory StoryPageId.fromJson(Map<String, dynamic> json) {
    return StoryPageId(
      imageUri: json['cover'],
      text: json['title'],
      storyId: json['storyId'],
    );
  }
}
