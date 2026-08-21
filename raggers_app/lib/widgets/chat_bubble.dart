import 'package:flutter/material.dart';
import 'package:raggers_app/models/chat_message_model.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;

  const ChatBubble({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    final isEmergency = message.type == MessageType.emergencyAlert;
    final isWarning = message.type == MessageType.warning;
    final isRecommendation = message.type == MessageType.medicalRecommendation;

    Color bubbleColor;
    if (isEmergency) {
      bubbleColor = Colors.red.shade100;
    } else if (isWarning) {
      bubbleColor = Colors.orange.shade100;
    } else if (isRecommendation) {
      bubbleColor = Colors.green.shade100;
    } else {
      bubbleColor = isUser ? Colors.blue.shade100 : Colors.grey.shade200;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            CircleAvatar(
              backgroundColor: isEmergency ? Colors.red :
              isWarning ? Colors.orange :
              isRecommendation ? Colors.green :
              Colors.blue.shade100,
              child: Icon(
                isEmergency ? Icons.warning :
                isWarning ? Icons.warning_amber :
                isRecommendation ? Icons.medical_information :
                Icons.medical_services,
                color: isEmergency ? Colors.red :
                isWarning ? Colors.orange :
                isRecommendation ? Colors.green :
                Colors.blue,
                size: 20,
              ),
            ),
            const SizedBox(width: 8),
          ],
          // REMOVED Expanded - now uses IntrinsicWidth or just Container with constraints
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.75, // Max 75% of screen
              minWidth: 60, // Minimum width for small messages
            ),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: bubbleColor,
              borderRadius: BorderRadius.circular(12),
              border: isEmergency || isWarning
                  ? Border.all(
                color: isEmergency ? Colors.red : Colors.orange,
                width: 2,
              )
                  : null,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  message.content,
                  style: TextStyle(
                    fontSize: 16,
                    color: isEmergency ? Colors.red.shade900 : null,
                    fontWeight: isEmergency ? FontWeight.bold : null,
                  ),
                  softWrap: true, // Allow text to wrap
                ),
                const SizedBox(height: 4),
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (isEmergency)
                      const Text(
                        '⚠️ URGENT',
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    if (isEmergency) const SizedBox(width: 8),
                    if (isWarning)
                      const Text(
                        '⚠️ WARNING',
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.orange,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    if (isWarning) const SizedBox(width: 8),
                    if (isRecommendation)
                      const Text(
                        '💊 RECOMMENDATION',
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    if (isRecommendation) const SizedBox(width: 8),
                    Text(
                      '${message.timestamp.hour.toString().padLeft(2, '0')}:${message.timestamp.minute.toString().padLeft(2, '0')}',
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 8),
            const CircleAvatar(
              backgroundColor: Colors.grey,
              child: Icon(Icons.person, color: Colors.white, size: 20),
            ),
          ],
        ],
      ),
    );
  }
}