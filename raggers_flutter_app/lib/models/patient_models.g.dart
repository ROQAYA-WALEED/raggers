// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'patient_models.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class PatientAdapter extends TypeAdapter<Patient> {
  @override
  final int typeId = 0;

  @override
  Patient read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return Patient(
      id: fields[0] as String,
      name: fields[1] as String,
      age: fields[2] as int,
      gender: fields[3] as String,
      bloodType: fields[4] as String,
      allergies: (fields[5] as List).cast<String>(),
      chronicConditions: (fields[6] as List).cast<String>(),
      currentMedications: fields[7] as String,
      medicalHistory: fields[8] as String,
      emergencyContact: fields[9] as String,
      emergencyPhone: fields[10] as String,
      address: fields[11] as String,
      occupation: fields[12] as String,
    );
  }

  @override
  void write(BinaryWriter writer, Patient obj) {
    writer
      ..writeByte(13)
      ..writeByte(0)
      ..write(obj.id)
      ..writeByte(1)
      ..write(obj.name)
      ..writeByte(2)
      ..write(obj.age)
      ..writeByte(3)
      ..write(obj.gender)
      ..writeByte(4)
      ..write(obj.bloodType)
      ..writeByte(5)
      ..write(obj.allergies)
      ..writeByte(6)
      ..write(obj.chronicConditions)
      ..writeByte(7)
      ..write(obj.currentMedications)
      ..writeByte(8)
      ..write(obj.medicalHistory)
      ..writeByte(9)
      ..write(obj.emergencyContact)
      ..writeByte(10)
      ..write(obj.emergencyPhone)
      ..writeByte(11)
      ..write(obj.address)
      ..writeByte(12)
      ..write(obj.occupation);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PatientAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
