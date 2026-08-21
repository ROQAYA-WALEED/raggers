import 'package:hive/hive.dart';

part 'vital_signs_model.g.dart';

@HiveType(typeId: 1)
class VitalSigns extends HiveObject {
  @HiveField(0)
  final DateTime timestamp;

  @HiveField(1)
  final double temperature;

  @HiveField(2)
  final int heartRate;

  @HiveField(3)
  final int respiratoryRate;

  @HiveField(4)
  final int systolicBP;

  @HiveField(5)
  final int diastolicBP;

  @HiveField(6)
  final int oxygenSaturation;

  @HiveField(7)
  final double weight;

  @HiveField(8)
  final double height;

  @HiveField(9)
  final String? notes;

  VitalSigns({
    required this.timestamp,
    required this.temperature,
    required this.heartRate,
    required this.respiratoryRate,
    required this.systolicBP,
    required this.diastolicBP,
    required this.oxygenSaturation,
    required this.weight,
    required this.height,
    this.notes,
  });

  bool get isNormal {
    return temperature >= 36.1 && temperature <= 37.2 &&
        heartRate >= 60 && heartRate <= 100 &&
        respiratoryRate >= 12 && respiratoryRate <= 20 &&
        systolicBP >= 90 && systolicBP <= 120 &&
        diastolicBP >= 60 && diastolicBP <= 80 &&
        oxygenSaturation >= 95 && oxygenSaturation <= 100;
  }

  List<String> get warnings {
    final List<String> warnings = [];
    if (temperature > 37.5) warnings.add('Fever detected');
    if (temperature > 39.0) warnings.add('High fever - seek medical attention');
    if (heartRate > 100) warnings.add('Tachycardia');
    if (heartRate < 60) warnings.add('Bradycardia');
    if (respiratoryRate > 20) warnings.add('Rapid breathing');
    if (respiratoryRate < 12) warnings.add('Slow breathing');
    if (systolicBP > 140 || diastolicBP > 90) warnings.add('High blood pressure');
    if (systolicBP < 90 || diastolicBP < 60) warnings.add('Low blood pressure');
    if (oxygenSaturation < 95) warnings.add('Low oxygen saturation');
    if (oxygenSaturation < 90) warnings.add('Critical oxygen level - seek immediate care');
    return warnings;
  }
}