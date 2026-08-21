// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'symptoms_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class SymptomAdapter extends TypeAdapter<Symptom> {
  @override
  final int typeId = 2;

  @override
  Symptom read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Symptom(
      id: fields[0] as String,
      name: fields[1] as String,
      severity: fields[2] as Severity,
      onsetDate: fields[3] as DateTime,
      duration: fields[4] as String,
      description: fields[5] as String?,
      triggers: (fields[6] as List).cast<String>(),
      relievingFactors: (fields[7] as List).cast<String>(),
      isActive: fields[8] as bool,
    );
  }

  @override
  void write(BinaryWriter writer, Symptom obj) {
    writer
      ..writeByte(9)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.severity)
      ..writeByte(3)
      ..write(obj.onsetDate)
      ..writeByte(4)
      ..write(obj.duration)
      ..writeByte(5)
      ..write(obj.description)
      ..writeByte(6)
      ..write(obj.triggers)
      ..writeByte(7)
      ..write(obj.relievingFactors)
      ..writeByte(8)
      ..write(obj.isActive);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SymptomAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

class SeverityAdapter extends TypeAdapter<Severity> {
  @override
  final int typeId = 4;

  @override
  Severity read(BinaryReader reader) {
    switch (reader.readByte()) {
      case 0:
        return Severity.mild;
      case 1:
        return Severity.moderate;
      case 2:
        return Severity.severe;
      case 3:
        return Severity.critical;
      default:
        return Severity.mild;
    }
  }

  @override
  void write(BinaryWriter writer, Severity obj) {
    switch (obj) {
      case Severity.mild:
        writer.writeByte(0);
        break;
      case Severity.moderate:
        writer.writeByte(1);
        break;
      case Severity.severe:
        writer.writeByte(2);
        break;
      case Severity.critical:
        writer.writeByte(3);
        break;
    }
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SeverityAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
