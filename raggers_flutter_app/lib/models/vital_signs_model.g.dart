// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'vital_signs_model.dart';

// **************************************************************************
// TypeAdapterGenerator
// **************************************************************************

class VitalSignsAdapter extends TypeAdapter<VitalSigns> {
  @override
  final int typeId = 1;

  @override
  VitalSigns read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return VitalSigns(
      timestamp: fields[0] as DateTime,
      temperature: fields[1] as double,
      heartRate: fields[2] as int,
      respiratoryRate: fields[3] as int,
      systolicBP: fields[4] as int,
      diastolicBP: fields[5] as int,
      oxygenSaturation: fields[6] as int,
      weight: fields[7] as double,
      height: fields[8] as double,
      notes: fields[9] as String?,
    );
  }

  @override
  void write(BinaryWriter writer, VitalSigns obj) {
    writer
      ..writeByte(10)
      ..writeByte(0)
      ..write(obj.timestamp)
      ..writeByte(1)
      ..write(obj.temperature)
      ..writeByte(2)
      ..write(obj.heartRate)
      ..writeByte(3)
      ..write(obj.respiratoryRate)
      ..writeByte(4)
      ..write(obj.systolicBP)
      ..writeByte(5)
      ..write(obj.diastolicBP)
      ..writeByte(6)
      ..write(obj.oxygenSaturation)
      ..writeByte(7)
      ..write(obj.weight)
      ..writeByte(8)
      ..write(obj.height)
      ..writeByte(9)
      ..write(obj.notes);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is VitalSignsAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}
