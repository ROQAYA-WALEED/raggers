import 'package:hive_flutter/hive_flutter.dart';
import 'package:path_provider/path_provider.dart' as path_provider;
import '../models/patient_models.dart';
import '../models/vital_signs_model.dart';
import '../models/symptoms_model.dart';
import 'package:raggers_app/models/chat_message_model.dart';

class DatabaseService {
  static const String patientBoxName = 'patient_box';
  static const String vitalsBoxName = 'vitals_box';
  static const String symptomsBoxName = 'symptoms_box';
  static const String chatBoxName = 'chat_box';

  late Box<Patient> _patientBox;
  late Box<VitalSigns> _vitalsBox;
  late Box<Symptom> _symptomsBox;
  late Box<ChatMessage> _chatBox;

  static final DatabaseService _instance = DatabaseService._internal();
  factory DatabaseService() => _instance;
  DatabaseService._internal();

  Future<void> init() async {
    final appDocumentDir = await path_provider.getApplicationDocumentsDirectory();
    Hive.init(appDocumentDir.path);

    // Register all adapters
    Hive.registerAdapter(PatientAdapter());
    Hive.registerAdapter(VitalSignsAdapter());
    Hive.registerAdapter(SymptomAdapter());
    Hive.registerAdapter(ChatMessageAdapter());
    Hive.registerAdapter(SeverityAdapter());
    Hive.registerAdapter(MessageTypeAdapter());
    // Citation is not a Hive type, we store it as part of ChatMessage

    _patientBox = await Hive.openBox<Patient>(patientBoxName);
    _vitalsBox = await Hive.openBox<VitalSigns>(vitalsBoxName);
    _symptomsBox = await Hive.openBox<Symptom>(symptomsBoxName);
    _chatBox = await Hive.openBox<ChatMessage>(chatBoxName);
  }

  // PATIENT METHODS
  Future<void> savePatient(Patient patient) async {
    await _patientBox.put(patient.id, patient);
  }

  Patient? getPatient(String id) {
    return _patientBox.get(id);
  }

  List<Patient> getAllPatients() {
    return _patientBox.values.toList();
  }

  Patient? getLatestPatient() {
    if (_patientBox.isEmpty) return null;
    return _patientBox.values.last;
  }

  Future<void> deletePatient(String id) async {
    await _patientBox.delete(id);
  }

  Future<void> clearAllPatients() async {
    await _patientBox.clear();
  }

  // VITALS METHODS
  Future<void> saveVitalSigns(VitalSigns vitals) async {
    final key = '${vitals.timestamp.millisecondsSinceEpoch}_${vitals.hashCode}';
    await _vitalsBox.put(key, vitals);
  }

  List<VitalSigns> getAllVitals() {
    final vitals = _vitalsBox.values.toList();
    vitals.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return vitals;
  }

  VitalSigns? getLatestVitals() {
    final vitals = _vitalsBox.values.toList();
    if (vitals.isEmpty) return null;
    vitals.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    return vitals.first;
  }

  Future<void> deleteAllVitals() async {
    await _vitalsBox.clear();
  }

  // SYMPTOMS METHODS
  Future<void> saveSymptom(Symptom symptom) async {
    await _symptomsBox.put(symptom.id, symptom);
  }

  Future<void> saveSymptoms(List<Symptom> symptoms) async {
    for (var symptom in symptoms) {
      await _symptomsBox.put(symptom.id, symptom);
    }
  }

  List<Symptom> getAllSymptoms() {
    return _symptomsBox.values.toList();
  }

  List<Symptom> getActiveSymptoms() {
    return _symptomsBox.values.where((s) => s.isActive).toList();
  }

  Symptom? getSymptom(String id) {
    return _symptomsBox.get(id);
  }

  Future<void> deleteSymptom(String id) async {
    await _symptomsBox.delete(id);
  }

  Future<void> clearAllSymptoms() async {
    await _symptomsBox.clear();
  }

  // CHAT METHODS
  Future<void> saveChatMessage(ChatMessage message) async {
    await _chatBox.put(message.id, message);
  }

  Future<void> saveChatMessages(List<ChatMessage> messages) async {
    for (var message in messages) {
      await _chatBox.put(message.id, message);
    }
  }

  List<ChatMessage> getAllChatMessages() {
    final messages = _chatBox.values.toList();
    messages.sort((a, b) => a.timestamp.compareTo(b.timestamp));
    return messages;
  }

  Future<void> deleteChatMessage(String id) async {
    await _chatBox.delete(id);
  }

  Future<void> clearAllChatMessages() async {
    await _chatBox.clear();
  }

  // UTILITY METHODS
  Future<void> clearAllData() async {
    await _patientBox.clear();
    await _vitalsBox.clear();
    await _symptomsBox.clear();
    await _chatBox.clear();
  }

  int get patientCount => _patientBox.length;
  int get vitalsCount => _vitalsBox.length;
  int get symptomsCount => _symptomsBox.length;
  int get chatCount => _chatBox.length;

  bool get hasData => _patientBox.isNotEmpty ||
      _vitalsBox.isNotEmpty ||
      _symptomsBox.isNotEmpty ||
      _chatBox.isNotEmpty;
}