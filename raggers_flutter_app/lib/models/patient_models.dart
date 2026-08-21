import 'package:hive/hive.dart';

part 'patient_models.g.dart';

@HiveType(typeId: 0)
class Patient extends HiveObject {
  @HiveField(0)
  final String id;

  @HiveField(1)
  String name;

  @HiveField(2)
  int age;

  @HiveField(3)
  String gender;

  @HiveField(4)
  String bloodType;

  @HiveField(5)
  List<String> allergies;

  @HiveField(6)
  List<String> chronicConditions;

  @HiveField(7)
  String currentMedications;

  @HiveField(8)
  String medicalHistory;

  @HiveField(9)
  String emergencyContact;

  @HiveField(10)
  String emergencyPhone;

  @HiveField(11)
  String address;

  @HiveField(12)
  String occupation;

  Patient({
    required this.id,
    required this.name,
    required this.age,
    required this.gender,
    this.bloodType = '',
    this.allergies = const [],
    this.chronicConditions = const [],
    this.currentMedications = '',
    this.medicalHistory = '',
    this.emergencyContact = '',
    this.emergencyPhone = '',
    this.address = '',
    this.occupation = '',
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'age': age,
    'gender': gender,
    'bloodType': bloodType,
    'allergies': allergies,
    'chronicConditions': chronicConditions,
    'currentMedications': currentMedications,
    'medicalHistory': medicalHistory,
    'emergencyContact': emergencyContact,
    'emergencyPhone': emergencyPhone,
    'address': address,
    'occupation': occupation,
  };

  factory Patient.fromJson(Map<String, dynamic> json) {
    return Patient(
      id: json['id'],
      name: json['name'],
      age: json['age'],
      gender: json['gender'],
      bloodType: json['bloodType'] ?? '',
      allergies: List<String>.from(json['allergies'] ?? []),
      chronicConditions: List<String>.from(json['chronicConditions'] ?? []),
      currentMedications: json['currentMedications'] ?? '',
      medicalHistory: json['medicalHistory'] ?? '',
      emergencyContact: json['emergencyContact'] ?? '',
      emergencyPhone: json['emergencyPhone'] ?? '',
      address: json['address'] ?? '',
      occupation: json['occupation'] ?? '',
    );
  }

  Patient copyWith({
    String? id,
    String? name,
    int? age,
    String? gender,
    String? bloodType,
    List<String>? allergies,
    List<String>? chronicConditions,
    String? currentMedications,
    String? medicalHistory,
    String? emergencyContact,
    String? emergencyPhone,
    String? address,
    String? occupation,
  }) {
    return Patient(
      id: id ?? this.id,
      name: name ?? this.name,
      age: age ?? this.age,
      gender: gender ?? this.gender,
      bloodType: bloodType ?? this.bloodType,
      allergies: allergies ?? this.allergies,
      chronicConditions: chronicConditions ?? this.chronicConditions,
      currentMedications: currentMedications ?? this.currentMedications,
      medicalHistory: medicalHistory ?? this.medicalHistory,
      emergencyContact: emergencyContact ?? this.emergencyContact,
      emergencyPhone: emergencyPhone ?? this.emergencyPhone,
      address: address ?? this.address,
      occupation: occupation ?? this.occupation,
    );
  }

  bool get hasAllergies => allergies.isNotEmpty;
  bool get hasChronicConditions => chronicConditions.isNotEmpty;
  bool get isComplete => name.isNotEmpty && age > 0 && gender.isNotEmpty;

  String get ageGroup {
    if (age < 2) return 'Infant';
    if (age < 12) return 'Child';
    if (age < 18) return 'Adolescent';
    if (age < 60) return 'Adult';
    return 'Senior';
  }

  String get bloodTypeDisplay => bloodType.isNotEmpty ? bloodType : 'Not specified';
  String get genderDisplay => gender.isNotEmpty ? gender : 'Not specified';
}

class PatientOptions {
  static const List<String> genders = ['Male', 'Female'];
  static const List<String> bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Unknown'];
  static const List<String> commonAllergies = [
    'Penicillin', 'Sulfa drugs', 'Aspirin', 'Ibuprofen', 'Codeine',
    'Latex', 'Peanuts', 'Shellfish', 'Dairy', 'Eggs', 'Soy', 'Wheat',
  ];
  static const List<String> commonConditions = [
    'Diabetes Type 1', 'Diabetes Type 2', 'Hypertension', 'Asthma',
    'COPD', 'Heart Disease', 'Kidney Disease', 'Liver Disease',
    'HIV/AIDS', 'Tuberculosis', 'Malaria (previous)', 'Anemia',
  ];
  static const List<String> commonMedications = [
    'Chloroquine', 'Artemisinin', 'Quinine', 'Mefloquine',
    'Doxycycline', 'Atovaquone-proguanil', 'Primaquine',
  ];
}