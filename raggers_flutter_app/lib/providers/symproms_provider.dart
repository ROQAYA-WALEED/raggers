import 'package:flutter/material.dart';
import 'package:raggers_app/models/symptoms_model.dart';
import '../services/database_service.dart';

class SymptomsProvider extends ChangeNotifier {
  final DatabaseService _db = DatabaseService();
  List<Symptom> _symptoms = [];

  List<Symptom> get symptoms => _symptoms;
  List<Symptom> get activeSymptoms => _symptoms.where((s) => s.isActive).toList();
  List<Symptom> get resolvedSymptoms => _symptoms.where((s) => !s.isActive).toList();

  SymptomsProvider() {
    _loadSymptoms();
  }

  Future<void> _loadSymptoms() async {
    _symptoms = _db.getAllSymptoms();
    notifyListeners();
  }

  List<Symptom> getSymptomsBySeverity(Severity severity) {
    return _symptoms.where((s) => s.severity == severity).toList();
  }

  List<Symptom> getRecentSymptoms(int days) {
    final cutoff = DateTime.now().subtract(Duration(days: days));
    return _symptoms.where((s) => s.onsetDate.isAfter(cutoff)).toList();
  }

  Future<void> addSymptom(Symptom symptom) async {
    _symptoms.add(symptom);
    await _db.saveSymptom(symptom);
    notifyListeners();
  }

  Future<void> addSymptoms(List<Symptom> newSymptoms) async {
    _symptoms.addAll(newSymptoms);
    await _db.saveSymptoms(newSymptoms);
    notifyListeners();
  }

  Future<void> updateSymptom(String id, Symptom updatedSymptom) async {
    final index = _symptoms.indexWhere((s) => s.id == id);
    if (index != -1) {
      _symptoms[index] = updatedSymptom;
      await _db.saveSymptom(updatedSymptom);
      notifyListeners();
    }
  }

  Future<void> removeSymptom(String id) async {
    _symptoms.removeWhere((s) => s.id == id);
    await _db.deleteSymptom(id);
    notifyListeners();
  }

  Future<void> resolveSymptom(String id) async {
    final index = _symptoms.indexWhere((s) => s.id == id);
    if (index != -1) {
      _symptoms[index] = _symptoms[index].copyWith(isActive: false);
      await _db.saveSymptom(_symptoms[index]);
      notifyListeners();
    }
  }

  Future<void> clearAllSymptoms() async {
    _symptoms.clear();
    await _db.clearAllSymptoms();
    notifyListeners();
  }

  String getSymptomSummary() {
    if (_symptoms.isEmpty) return 'No symptoms reported';

    final active = activeSymptoms;
    if (active.isEmpty) return 'All symptoms resolved';

    final severeSymptoms = active.where((s) =>
    s.severity == Severity.severe || s.severity == Severity.critical
    ).toList();

    String summary = 'Active symptoms: ${active.length}\n';
    if (severeSymptoms.isNotEmpty) {
      summary += '⚠️ Severe: ${severeSymptoms.map((s) => s.name).join(', ')}\n';
    }
    summary += 'Most recent: ${active.last.name} (${active.last.severity.label})';
    return summary;
  }

  Future<void> refresh() async {
    await _loadSymptoms();
  }
}