import 'package:flutter/material.dart';
import 'package:raggers_app/models/patient_models.dart';
import '../services/database_service.dart';

class PatientProvider extends ChangeNotifier {
  Patient? _currentPatient;
  final DatabaseService _db = DatabaseService();

  Patient? get currentPatient => _currentPatient;

  PatientProvider() {
    _loadLatestPatient();
  }

  Future<void> _loadLatestPatient() async {
    _currentPatient = _db.getLatestPatient();
    notifyListeners();
  }

  Future<void> updatePatient(Patient patient) async {
    _currentPatient = patient;
    await _db.savePatient(patient);
    notifyListeners();
  }

  Future<void> updatePatientField(String field, dynamic value) async {
    if (_currentPatient == null) return;

    final updatedPatient = _currentPatient!.copyWith(
      name: field == 'name' ? value as String : _currentPatient!.name,
      age: field == 'age' ? value as int : _currentPatient!.age,
      gender: field == 'gender' ? value as String : _currentPatient!.gender,
      bloodType: field == 'bloodType' ? value as String : _currentPatient!.bloodType,
      allergies: field == 'allergies' ? value as List<String> : _currentPatient!.allergies,
      chronicConditions: field == 'chronicConditions' ? value as List<String> : _currentPatient!.chronicConditions,
      currentMedications: field == 'currentMedications' ? value as String : _currentPatient!.currentMedications,
      medicalHistory: field == 'medicalHistory' ? value as String : _currentPatient!.medicalHistory,
      emergencyContact: field == 'emergencyContact' ? value as String : _currentPatient!.emergencyContact,
      emergencyPhone: field == 'emergencyPhone' ? value as String : _currentPatient!.emergencyPhone,
      address: field == 'address' ? value as String : _currentPatient!.address,
      occupation: field == 'occupation' ? value as String : _currentPatient!.occupation,
    );

    _currentPatient = updatedPatient;
    await _db.savePatient(updatedPatient);
    notifyListeners();
  }

  Future<void> createNewPatient({String? name}) async {
    final patient = Patient(
      id: 'PAT-${DateTime.now().millisecondsSinceEpoch}',
      name: name ?? 'New Patient',
      age: 0,
      gender: '',
    );
    _currentPatient = patient;
    await _db.savePatient(patient);
    notifyListeners();
  }

  Future<void> resetPatient() async {
    _currentPatient = null;
    // Optionally clear all data
    // await _db.clearAllData();
    notifyListeners();
  }

  String getPatientSummary() {
    if (_currentPatient == null) return 'No patient loaded';
    final p = _currentPatient!;
    return '''
Name: ${p.name}
Age: ${p.age} (${p.ageGroup})
Gender: ${p.genderDisplay}
Blood Type: ${p.bloodTypeDisplay}
${p.hasAllergies ? '⚠️ Allergies: ${p.allergies.join(", ")}' : 'No allergies reported'}
${p.hasChronicConditions ? '📋 Conditions: ${p.chronicConditions.join(", ")}' : 'No chronic conditions'}
''';
  }

  bool get hasPatient => _currentPatient != null;
}