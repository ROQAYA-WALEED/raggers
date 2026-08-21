import 'package:hive/hive.dart';
import 'package:flutter/material.dart';

part 'symptoms_model.g.dart';

@HiveType(typeId: 4)  // Add this for enum
enum Severity {
  @HiveField(0)  // Add this for each value
  mild('Mild', Colors.green),
  @HiveField(1)
  moderate('Moderate', Colors.orange),
  @HiveField(2)
  severe('Severe', Colors.red),
  @HiveField(3)
  critical('Critical', Colors.purple);

  final String label;
  final Color color;
  const Severity(this.label, this.color);
}

@HiveType(typeId: 2)
class Symptom extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  final String name;

  @HiveField(2)
  final Severity severity;

  @HiveField(3)
  final DateTime onsetDate;

  @HiveField(4)
  final String duration;

  @HiveField(5)
  final String? description;

  @HiveField(6)
  final List<String> triggers;

  @HiveField(7)
  final List<String> relievingFactors;

  @HiveField(8)
  final bool isActive;

  Symptom({
    required this.id,
    required this.name,
    required this.severity,
    required this.onsetDate,
    required this.duration,
    this.description,
    this.triggers = const [],
    this.relievingFactors = const [],
    this.isActive = true,
  });

  Symptom copyWith({
    String? id,
    String? name,
    Severity? severity,
    DateTime? onsetDate,
    String? duration,
    String? description,
    List<String>? triggers,
    List<String>? relievingFactors,
    bool? isActive,
  }) {
    return Symptom(
      id: id ?? this.id,
      name: name ?? this.name,
      severity: severity ?? this.severity,
      onsetDate: onsetDate ?? this.onsetDate,
      duration: duration ?? this.duration,
      description: description ?? this.description,
      triggers: triggers ?? this.triggers,
      relievingFactors: relievingFactors ?? this.relievingFactors,
      isActive: isActive ?? this.isActive,
    );
  }
}

class CommonSymptoms {
  static const List<String> malariaSymptoms = [
    'Fever', 'Chills', 'Sweating', 'Headache', 'Nausea',
    'Vomiting', 'Diarrhea', 'Muscle Pain', 'Joint Pain',
    'Fatigue', 'Weakness', 'Pale Skin', 'Jaundice',
    'Dark Urine', 'Anemia', 'Rapid Heartbeat', 'Rapid Breathing',
    'Confusion', 'Seizures', 'Cough', 'Chest Pain',
    'Difficulty Breathing',
  ];

  static const List<String> generalSymptoms = [
    'Dizziness', 'Loss of Appetite', 'Weight Loss',
    'Abdominal Pain', 'Back Pain', 'Skin Rash', 'Itching',
    'Swelling', 'Sleep Problems', 'Anxiety',
  ];
}