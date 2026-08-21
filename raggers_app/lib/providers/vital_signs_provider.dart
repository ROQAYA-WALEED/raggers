import 'package:flutter/material.dart';
import 'package:raggers_app/models/vital_signs_model.dart';
import '../services/database_service.dart';

class VitalSignsProvider extends ChangeNotifier {
  final DatabaseService _db = DatabaseService();
  List<VitalSigns> _vitalSignsHistory = [];

  List<VitalSigns> get vitalSignsHistory => _vitalSignsHistory;
  VitalSigns? get latestVitalSigns => _vitalSignsHistory.isNotEmpty ? _vitalSignsHistory.last : null;

  VitalSignsProvider() {
    _loadVitals();
  }

  Future<void> _loadVitals() async {
    _vitalSignsHistory = _db.getAllVitals();
    // Sort by timestamp descending (newest first)
    _vitalSignsHistory.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    notifyListeners();
  }

  Future<void> addVitalSigns(VitalSigns vitalSigns) async {
    _vitalSignsHistory.add(vitalSigns);
    await _db.saveVitalSigns(vitalSigns);
    notifyListeners();
  }

  Future<void> clearHistory() async {
    _vitalSignsHistory.clear();
    await _db.deleteAllVitals();
    notifyListeners();
  }

  List<VitalSigns> getVitalsForDateRange(DateTime start, DateTime end) {
    return _vitalSignsHistory.where((v) =>
    v.timestamp.isAfter(start) && v.timestamp.isBefore(end)
    ).toList();
  }

  Future<void> refresh() async {
    await _loadVitals();
  }
}