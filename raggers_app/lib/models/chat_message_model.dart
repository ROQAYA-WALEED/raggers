import 'package:hive/hive.dart';

part 'chat_message_model.g.dart';

@HiveType(typeId: 5)
enum MessageType {
  @HiveField(0)
  text,
  @HiveField(1)
  medicalRecommendation,
  @HiveField(2)
  emergencyAlert,
  @HiveField(3)
  warning,
}

class Citation {
  final String id;
  final String title;
  final String source;
  final String? url;
  final String? excerpt;
  final DateTime? date;

  Citation({
    required this.id,
    required this.title,
    required this.source,
    this.url,
    this.excerpt,
    this.date,
  });

  factory Citation.fromJson(Map<String, dynamic> json) {
    return Citation(
      id: json['id'] ?? 'cit_${DateTime.now().millisecondsSinceEpoch}',
      title: json['title'] ?? json['source'] ?? 'Medical Reference',
      source: json['source'] ?? 'Unknown Source',
      url: json['url'],
      excerpt: json['excerpt'],
      date: json['date'] != null ? DateTime.parse(json['date']) : null,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'source': source,
    'url': url,
    'excerpt': excerpt,
    'date': date?.toIso8601String(),
  };
}

@HiveType(typeId: 3)
class ChatMessage extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String content;

  @HiveField(2)
  final bool isUser;

  @HiveField(3)
  final DateTime timestamp;

  @HiveField(4)
  final MessageType type;

  // Store citations as List<Map> for Hive
  @HiveField(5)
  final List<Map<String, dynamic>>? _citationsJson;

  ChatMessage({
    required this.id,
    required this.content,
    required this.isUser,
    required this.timestamp,
    this.type = MessageType.text,
    List<Citation>? citations,
  }) : _citationsJson = citations?.map((c) => c.toJson()).toList();

  // Get citations as List<Citation>
  List<Citation>? get citations {
    if (_citationsJson == null) return null;
    return _citationsJson!.map((json) => Citation.fromJson(json)).toList();
  }

  bool get hasCitations => _citationsJson != null && _citationsJson!.isNotEmpty;
  int get citationCount => _citationsJson?.length ?? 0;
}