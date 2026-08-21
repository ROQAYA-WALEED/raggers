import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:raggers_app/models/chat_message_model.dart';
import 'package:raggers_app/models/symptoms_model.dart';
import 'package:raggers_app/models/vital_signs_model.dart';
import '../widgets/chat_bubble.dart';
import '../providers/patient_provider.dart';
import '../providers/vital_signs_provider.dart';
import 'package:raggers_app/providers/symproms_provider.dart';
import '../providers/chat_provider.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  bool _initialLoadDone = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeChat();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_initialLoadDone) {
      _initializeChat();
    }
  }

  Future<void> _initializeChat() async {
    if (_initialLoadDone) return;
    _initialLoadDone = true;

    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    await chatProvider.refresh();

    if (chatProvider.messages.isEmpty) {
      await _addWelcomeMessages(chatProvider);
    }

    _scrollToBottom();
  }

  Future<void> _addWelcomeMessages(ChatProvider chatProvider) async {
    await chatProvider.addMessage(
      content: 'Welcome to the Malaria Medical Assistant. How can I help you today?',
      isUser: false,
      type: MessageType.text,
    );

    Future.delayed(const Duration(milliseconds: 300), () {
      _addPatientSummary();
    });
  }

  void _addPatientSummary() {
    final patientProvider = Provider.of<PatientProvider>(context, listen: false);
    final vitalProvider = Provider.of<VitalSignsProvider>(context, listen: false);
    final symptomProvider = Provider.of<SymptomsProvider>(context, listen: false);
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);

    final patient = patientProvider.currentPatient;
    if (patient == null) return;

    final latestVitals = vitalProvider.latestVitalSigns;
    final activeSymptoms = symptomProvider.activeSymptoms;

    String summary = '📋 Patient Summary\n\n';
    summary += 'Name: ${patient.name}\n';
    summary += 'Age: ${patient.age} years\n';
    summary += 'Gender: ${patient.genderDisplay}\n\n';

    if (latestVitals != null) {
      summary += 'Recent Vitals:\n';
      summary += '• Temp: ${latestVitals.temperature.toStringAsFixed(1)}°C\n';
      summary += '• HR: ${latestVitals.heartRate} bpm\n';
      summary += '• BP: ${latestVitals.systolicBP}/${latestVitals.diastolicBP}\n';
      summary += '• O2: ${latestVitals.oxygenSaturation}%\n\n';
    }

    if (activeSymptoms.isNotEmpty) {
      summary += 'Active Symptoms (${activeSymptoms.length}):\n';
      for (var symptom in activeSymptoms) {
        summary += '• ${symptom.name} (${symptom.severity.label})\n';
      }
      summary += '\n';
    }

    if (patient.hasAllergies) {
      summary += 'Allergies: ${patient.allergies.join(", ")}\n';
    }

    if (patient.currentMedications.isNotEmpty) {
      summary += 'Medications: ${patient.currentMedications}\n';
    }

    chatProvider.addMessage(
      content: summary,
      isUser: false,
      type: MessageType.medicalRecommendation,
    );

    _scrollToBottom();
  }

  void _sendMessage() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    final patientProvider = Provider.of<PatientProvider>(context, listen: false);
    final vitalProvider = Provider.of<VitalSignsProvider>(context, listen: false);
    final symptomProvider = Provider.of<SymptomsProvider>(context, listen: false);

    // Add user message
    chatProvider.addMessage(
      content: text,
      isUser: true,
    );
    _messageController.clear();

    // Check if patient exists
    final patient = patientProvider.currentPatient;
    if (patient == null) {
      chatProvider.addMessage(
        content: '⚠️ Please add patient information first. Go to the Patient tab to create a patient profile.',
        isUser: false,
        type: MessageType.warning,
      );
      _scrollToBottom();
      return;
    }

    // Prepare patient data for API
    final patientData = {
      'patient': patient,
      'vitals': vitalProvider.vitalSignsHistory,
      'symptoms': symptomProvider.symptoms,
    };

    // Send to API
    chatProvider.sendToApi(
      question: text,
      patientData: patientData,
    ).then((_) {
      _scrollToBottom();
    });

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _clearChat() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Chat'),
        content: const Text('This will clear all chat messages. Continue?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              final chatProvider = Provider.of<ChatProvider>(context, listen: false);
              chatProvider.clearMessages();
              Future.delayed(const Duration(milliseconds: 100), () {
                _addWelcomeMessages(chatProvider);
              });
              Navigator.pop(context);
            },
            child: const Text('Clear', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  bool _hasAbnormalVitals(VitalSigns? vitals) {
    if (vitals == null) return false;
    if (vitals.temperature < 36.1 || vitals.temperature > 37.2) return true;
    if (vitals.heartRate < 60 || vitals.heartRate > 100) return true;
    if (vitals.respiratoryRate < 12 || vitals.respiratoryRate > 20) return true;
    if (vitals.systolicBP < 90 || vitals.systolicBP > 120) return true;
    if (vitals.diastolicBP < 60 || vitals.diastolicBP > 80) return true;
    if (vitals.oxygenSaturation < 95 || vitals.oxygenSaturation > 100) return true;
    return false;
  }

  @override
  Widget build(BuildContext context) {
    final patientProvider = Provider.of<PatientProvider>(context);
    final vitalProvider = Provider.of<VitalSignsProvider>(context);
    final symptomProvider = Provider.of<SymptomsProvider>(context);
    final chatProvider = Provider.of<ChatProvider>(context);

    final patient = patientProvider.currentPatient;
    final vitals = vitalProvider.latestVitalSigns;
    final symptoms = symptomProvider.activeSymptoms;
    final hasAbnormal = _hasAbnormalVitals(vitals);
    final messages = chatProvider.messages;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Malaria Medical Assistant'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          if (patient != null)
            Container(
              margin: const EdgeInsets.only(right: 8),
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.person, size: 14, color: Colors.white),
                  const SizedBox(width: 4),
                  Text(
                    patient.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          Container(
            margin: const EdgeInsets.only(right: 8),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: chatProvider.isApiAvailable
                  ? Colors.green.withOpacity(0.3)
                  : Colors.red.withOpacity(0.3),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  chatProvider.isApiAvailable ? Icons.cloud_done : Icons.cloud_off,
                  size: 14,
                  color: chatProvider.isApiAvailable ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 4),
                Text(
                  chatProvider.isApiAvailable ? 'API ✓' : 'API ✗',
                  style: TextStyle(
                    fontSize: 11,
                    color: chatProvider.isApiAvailable ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: _clearChat,
            tooltip: 'Clear Chat',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              final chatProvider = Provider.of<ChatProvider>(context, listen: false);
              chatProvider.refresh();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Chat refreshed'),
                  duration: Duration(seconds: 1),
                ),
              );
            },
            tooltip: 'Refresh Chat',
          ),
        ],
      ),
      body: Column(
        children: [
          if (patient != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              color: hasAbnormal ? Colors.red.shade50 : Colors.blue.shade50,
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatusItem(
                    label: '${patient.age}yrs',
                    icon: Icons.calendar_today,
                    color: Colors.blue,
                    tooltip: 'Age: ${patient.age} years\nGender: ${patient.genderDisplay}',
                  ),
                  _buildStatusItem(
                    label: vitals != null ? '${vitals.temperature.toStringAsFixed(1)}°C' : '--',
                    icon: Icons.thermostat,
                    color: vitals != null && (vitals.temperature < 36.1 || vitals.temperature > 37.2)
                        ? Colors.red
                        : Colors.orange,
                    tooltip: vitals != null
                        ? 'Temperature: ${vitals.temperature.toStringAsFixed(1)}°C\nNormal: 36.1-37.2°C'
                        : 'No temperature recorded',
                  ),
                  _buildStatusItem(
                    label: vitals != null ? '${vitals.heartRate}bpm' : '--',
                    icon: Icons.favorite,
                    color: vitals != null && (vitals.heartRate < 60 || vitals.heartRate > 100)
                        ? Colors.red
                        : Colors.red,
                    tooltip: vitals != null
                        ? 'Heart Rate: ${vitals.heartRate} bpm\nNormal: 60-100 bpm'
                        : 'No heart rate recorded',
                  ),
                  _buildStatusItem(
                    label: vitals != null ? '${vitals.systolicBP}/${vitals.diastolicBP}' : '--',
                    icon: Icons.bloodtype,
                    color: vitals != null && (vitals.systolicBP < 90 || vitals.systolicBP > 120 ||
                        vitals.diastolicBP < 60 || vitals.diastolicBP > 80)
                        ? Colors.red
                        : Colors.purple,
                    tooltip: vitals != null
                        ? 'Blood Pressure: ${vitals.systolicBP}/${vitals.diastolicBP}\nNormal: 90-120/60-80'
                        : 'No blood pressure recorded',
                  ),
                  _buildStatusItem(
                    label: vitals != null ? '${vitals.oxygenSaturation}%' : '--',
                    icon: Icons.water,
                    color: vitals != null && vitals.oxygenSaturation < 95
                        ? Colors.red
                        : Colors.blue,
                    tooltip: vitals != null
                        ? 'O2 Saturation: ${vitals.oxygenSaturation}%\nNormal: 95-100%'
                        : 'No O2 saturation recorded',
                  ),
                  _buildStatusItem(
                    label: symptoms.isNotEmpty ? '${symptoms.length}' : '0',
                    icon: Icons.healing,
                    color: symptoms.any((s) => s.severity == Severity.severe || s.severity == Severity.critical)
                        ? Colors.red
                        : symptoms.isNotEmpty ? Colors.orange : Colors.grey,
                    tooltip: symptoms.isNotEmpty
                        ? 'Active Symptoms (${symptoms.length})'
                        : 'No active symptoms',
                  ),
                ],
              ),
            ),
          Expanded(
            child: messages.isEmpty
                ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.chat, size: 48, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No messages yet',
                    style: TextStyle(color: Colors.grey),
                  ),
                  Text(
                    'Start a conversation below',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            )
                : ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(16),
              itemCount: messages.length,
              itemBuilder: (context, index) {
                return ChatBubble(message: messages[index]);
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade50,
              border: Border(
                top: BorderSide(color: Colors.grey.shade300),
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    decoration: InputDecoration(
                      hintText: patient != null
                          ? 'Ask about ${patient.name}\'s condition...'
                          : 'Type your message...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(24),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: Colors.white,
                      contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                    ),
                    onSubmitted: (_) => _sendMessage(),
                    textInputAction: TextInputAction.send,
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  decoration: BoxDecoration(
                    color: chatProvider.isProcessing ? Colors.grey : Colors.blue.shade700,
                    shape: BoxShape.circle,
                  ),
                  child: IconButton(
                    icon: chatProvider.isProcessing
                        ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                        : const Icon(Icons.send, color: Colors.white),
                    onPressed: chatProvider.isProcessing ? null : _sendMessage,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusItem({
    required String label,
    required IconData icon,
    required Color color,
    required String tooltip,
  }) {
    return Tooltip(
      message: tooltip,
      preferBelow: false,
      showDuration: const Duration(seconds: 3),
      waitDuration: const Duration(milliseconds: 500),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}