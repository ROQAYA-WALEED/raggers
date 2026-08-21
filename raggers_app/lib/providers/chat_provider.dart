import 'package:flutter/material.dart';
import 'package:raggers_app/models/chat_message_model.dart';
import '../services/database_service.dart';
import '../services/api_service.dart';

class ChatProvider extends ChangeNotifier {
  final DatabaseService _db = DatabaseService();
  final ApiService _api = ApiService();
  List<ChatMessage> _messages = [];
  bool _isProcessing = false;
  bool _isApiAvailable = false;
  bool _isLoading = false;

  List<ChatMessage> get messages => _messages;
  bool get isProcessing => _isProcessing;
  bool get isApiAvailable => _isApiAvailable;
  bool get isLoading => _isLoading;

  ChatProvider() {
    _checkApiAvailability();
  }

  Future<void> loadMessages() async {
    if (_isLoading) return;
    _isLoading = true;

    try {
      _messages = _db.getAllChatMessages();
      notifyListeners();
    } finally {
      _isLoading = false;
    }
  }

  Future<void> refresh() async {
    await loadMessages();
    await _checkApiAvailability();
  }

  Future<void> _checkApiAvailability() async {
    _isApiAvailable = await _api.checkApiAvailability();
    notifyListeners();
  }

  Future<void> sendToApi({
    required String question,
    required Map<String, dynamic> patientData,
  }) async {
    if (_isProcessing) return;

    _isProcessing = true;
    notifyListeners();

    try {
      print('📤 ChatProvider: Sending to API...');
      final response = await _api.sendQuery(
        question: question,
        patient: patientData['patient'],
        vitalsHistory: patientData['vitals'],
        symptoms: patientData['symptoms'],
      );

      print('📥 ChatProvider: Received response: $response');

      // Convert citations from List<dynamic> to List<Citation>
      List<Citation>? citations;
      if (response['citations'] != null && response['citations'] is List) {
        final citationList = response['citations'] as List;
        citations = citationList.map((c) {
          if (c is Citation) {
            return c;
          } else if (c is Map<String, dynamic>) {
            return Citation.fromJson(c);
          } else if (c is String) {
            return Citation(
              id: 'cit_${DateTime.now().millisecondsSinceEpoch}',
              title: c,
              source: 'Medical Reference',
            );
          } else {
            return Citation(
              id: 'cit_${DateTime.now().millisecondsSinceEpoch}',
              title: c.toString(),
              source: 'Medical Reference',
            );
          }
        }).toList();
      }

      // Add AI response
      await addMessage(
        content: response['content'],
        isUser: false,
        type: _determineMessageType(response),
        citations: citations,
      );

      // If blocked, show additional info
      if (response['was_blocked'] == true) {
        await addMessage(
          content: '⚠️ Note: ${response['block_reason'] ?? 'This question could not be answered based on available medical documents.'}',
          isUser: false,
          type: MessageType.warning,
        );
      }
    } catch (e) {
      print('❌ ChatProvider Error: $e');
      await addMessage(
        content: '❌ Error: Unable to process your request. Please try again later.',
        isUser: false,
        type: MessageType.warning,
      );
    } finally {
      _isProcessing = false;
      notifyListeners();
    }
  }

  Future<void> addMessage({
    required String content,
    required bool isUser,
    MessageType type = MessageType.text,
    List<Citation>? citations,
  }) async {
    print('📝 ChatProvider: Adding message - isUser: $isUser, content: ${content.substring(0, content.length > 100 ? 100 : content.length)}...');

    final message = ChatMessage(
      id: 'msg_${DateTime.now().millisecondsSinceEpoch}',
      content: content,
      isUser: isUser,
      timestamp: DateTime.now(),
      type: type,
      citations: citations,
    );
    _messages.add(message);
    await _db.saveChatMessage(message);
    notifyListeners();
  }

  Future<void> addMessages(List<ChatMessage> messages) async {
    _messages.addAll(messages);
    await _db.saveChatMessages(messages);
    notifyListeners();
  }

  Future<void> clearMessages() async {
    _messages.clear();
    await _db.clearAllChatMessages();
    notifyListeners();
  }

  MessageType _determineMessageType(Map<String, dynamic> response) {
    if (response['was_blocked'] == true) {
      return MessageType.warning;
    }
    if (response['confidence'] == 'insufficient') {
      return MessageType.warning;
    }
    if (response['recommendation']?.isNotEmpty == true) {
      return MessageType.medicalRecommendation;
    }
    return MessageType.text;
  }

  List<ChatMessage> getMessagesWithCitations() {
    return _messages.where((m) => m.hasCitations).toList();
  }

  List<ChatMessage> getMessagesForDateRange(DateTime start, DateTime end) {
    return _messages.where((m) =>
    m.timestamp.isAfter(start) && m.timestamp.isBefore(end)
    ).toList();
  }

  List<ChatMessage> getUserMessages() {
    return _messages.where((m) => m.isUser).toList();
  }

  List<ChatMessage> getAIMessages() {
    return _messages.where((m) => !m.isUser).toList();
  }

  List<ChatMessage> getLastMessages(int count) {
    if (_messages.length <= count) return _messages;
    return _messages.sublist(_messages.length - count);
  }

  Future<void> clearOldMessages(int days) async {
    final cutoff = DateTime.now().subtract(Duration(days: days));
    final toRemove = _messages.where((m) => m.timestamp.isBefore(cutoff)).toList();

    for (var message in toRemove) {
      _messages.remove(message);
      await _db.deleteChatMessage(message.id);
    }
    notifyListeners();
  }
}