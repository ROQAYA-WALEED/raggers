import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:raggers_app/models/patient_models.dart';
import '../providers/patient_provider.dart';
import '../providers/vital_signs_provider.dart';
import 'package:raggers_app/providers/symproms_provider.dart';
import '../widgets/patient_card.dart';
import '../main.dart';

class PatientScreen extends StatelessWidget {
  const PatientScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Patient Information'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {
              _showEditPatientDialog(context);
            },
            tooltip: 'Edit Patient',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              // Refresh view
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Refreshed patient data'),
                  duration: Duration(seconds: 1),
                ),
              );
            },
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Consumer<PatientProvider>(
        builder: (context, patientProvider, child) {
          final patient = patientProvider.currentPatient;

          if (patient == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.person_off,
                    size: 64,
                    color: Colors.grey.shade400,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No patient loaded',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Create a new patient or load existing',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade400,
                    ),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () {
                      patientProvider.createNewPatient(name: 'New Patient');
                      _showEditPatientDialog(context);
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('Create Patient'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue.shade700,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Patient Card
                PatientCard(
                  onEdit: () => _showEditPatientDialog(context),
                ),
                const SizedBox(height: 16),

                // Quick stats
                _buildQuickStats(context, patient),
                const SizedBox(height: 16),

                // Patient summary sections
                _buildSection(
                  title: 'Medical Summary',
                  icon: Icons.medical_information,
                  child: Column(
                    children: [
                      _buildSummaryItem(
                        'Allergies',
                        patient.hasAllergies
                            ? patient.allergies.join(', ')
                            : 'None reported',
                        patient.hasAllergies ? Colors.orange : Colors.grey,
                      ),
                      const Divider(height: 1),
                      _buildSummaryItem(
                        'Chronic Conditions',
                        patient.hasChronicConditions
                            ? patient.chronicConditions.join(', ')
                            : 'None reported',
                        patient.hasChronicConditions ? Colors.purple : Colors.grey,
                      ),
                      const Divider(height: 1),
                      _buildSummaryItem(
                        'Current Medications',
                        patient.currentMedications.isNotEmpty
                            ? patient.currentMedications
                            : 'None reported',
                        patient.currentMedications.isNotEmpty ? Colors.blue : Colors.grey,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Emergency contact
                _buildSection(
                  title: 'Emergency Contact',
                  icon: Icons.emergency,
                  child: Column(
                    children: [
                      _buildSummaryItem(
                        'Contact',
                        patient.emergencyContact.isNotEmpty
                            ? patient.emergencyContact
                            : 'Not set',
                        patient.emergencyContact.isNotEmpty ? Colors.red : Colors.grey,
                      ),
                      const Divider(height: 1),
                      _buildSummaryItem(
                        'Phone',
                        patient.emergencyPhone.isNotEmpty
                            ? patient.emergencyPhone
                            : 'Not set',
                        patient.emergencyPhone.isNotEmpty ? Colors.red : Colors.grey,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // Address and occupation
                _buildSection(
                  title: 'Additional Information',
                  icon: Icons.info,
                  child: Column(
                    children: [
                      _buildSummaryItem(
                        'Occupation',
                        patient.occupation.isNotEmpty ? patient.occupation : 'Not set',
                        patient.occupation.isNotEmpty ? Colors.green : Colors.grey,
                      ),
                      const Divider(height: 1),
                      _buildSummaryItem(
                        'Address',
                        patient.address.isNotEmpty ? patient.address : 'Not set',
                        patient.address.isNotEmpty ? Colors.grey : Colors.grey,
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),

                // Action buttons
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () {
                          _showPatientSummary(context);
                        },
                        icon: const Icon(Icons.file_copy),
                        label: const Text('View Summary'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () {
                          _showExportDialog(context);
                        },
                        icon: const Icon(Icons.ios_share_rounded),
                        label: const Text('Export Data'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      _confirmReset(context);
                    },
                    icon: const Icon(Icons.delete_outline),
                    label: const Text('Reset Patient Data'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.red,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildQuickStats(BuildContext context, Patient patient) {
    final vitalProvider = Provider.of<VitalSignsProvider>(context);
    final symptomProvider = Provider.of<SymptomsProvider>(context);

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildStatItem(
              'Vitals',
              '${vitalProvider.vitalSignsHistory.length}',
              Icons.medical_services,
              Colors.blue,
              onTap: () {
                // Navigate to vitals tab
                _navigateToTab(context, 1);
              },
            ),
            Container(
              width: 1,
              height: 40,
              color: Colors.grey.shade300,
            ),
            _buildStatItem(
              'Symptoms',
              '${symptomProvider.activeSymptoms.length}',
              Icons.healing,
              Colors.orange,
              onTap: () {
                // Navigate to symptoms tab
                _navigateToTab(context, 2);
              },
            ),
            Container(
              width: 1,
              height: 40,
              color: Colors.grey.shade300,
            ),
            _buildStatItem(
              'Status',
              patient.isComplete ? 'Complete' : 'Incomplete',
              patient.isComplete ? Icons.check_circle : Icons.warning,
              patient.isComplete ? Colors.green : Colors.orange,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(
      String label,
      String value,
      IconData icon,
      Color color, {
        VoidCallback? onTap,
      }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection({
    required String title,
    required IconData icon,
    required Widget child,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: Colors.blue.shade700),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            child,
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade600,
                fontSize: 14,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: valueColor,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGenderIcon(String gender) {
    final lowerGender = gender.toLowerCase();
    IconData icon;
    Color color;

    if (lowerGender.contains('male') || lowerGender == 'm') {
      icon = Icons.male;
      color = Colors.blue;
    } else if (lowerGender.contains('female') || lowerGender == 'f') {
      icon = Icons.female;
      color = Colors.pink;
    } else {
      icon = Icons.person_outline;
      color = Colors.grey;
    }

    return Icon(icon, color: color);
  }

  void _showEditPatientDialog(BuildContext context) {
    final provider = Provider.of<PatientProvider>(context, listen: false);
    final patient = provider.currentPatient;

    if (patient == null) return;

    final nameController = TextEditingController(text: patient.name);
    final ageController = TextEditingController(text: patient.age.toString());
    final bloodTypeController = TextEditingController(text: patient.bloodType);
    final medicationsController = TextEditingController(text: patient.currentMedications);
    final historyController = TextEditingController(text: patient.medicalHistory);
    final emergencyContactController = TextEditingController(text: patient.emergencyContact);
    final emergencyPhoneController = TextEditingController(text: patient.emergencyPhone);
    final addressController = TextEditingController(text: patient.address);
    final occupationController = TextEditingController(text: patient.occupation);

    String selectedGender = patient.gender;
    List<String> selectedAllergies = List.from(patient.allergies);
    List<String> selectedConditions = List.from(patient.chronicConditions);

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) {
          return AlertDialog(
            title: const Text('Edit Patient Information'),
            content: SingleChildScrollView(
              child: SizedBox(
                width: 500,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Basic Info
                    TextField(
                      controller: nameController,
                      decoration: const InputDecoration(
                        labelText: 'Full Name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: ageController,
                            decoration: const InputDecoration(
                              labelText: 'Age',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.calendar_today),
                            ),
                            keyboardType: TextInputType.number,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: // In _showEditPatientDialog method, update the gender dropdown
                          DropdownButtonFormField<String>(
                            value: selectedGender.isNotEmpty ? selectedGender : null,
                            decoration: const InputDecoration(
                              labelText: 'Gender',
                              border: OutlineInputBorder(),
                              prefixIcon: Icon(Icons.person_outline),
                            ),
                            items: PatientOptions.genders.map((gender) {
                              IconData icon;
                              if (gender.toLowerCase().contains('female')) {
                                icon = Icons.female;
                              } else if (gender.toLowerCase().contains('male')) {
                                icon = Icons.male;
                              } else {
                                icon = Icons.person_outline;
                              }

                              return DropdownMenuItem(
                                value: gender,
                                child: Row(
                                  children: [
                                    Icon(icon, size: 20),
                                    const SizedBox(width: 8),
                                    Text(gender),
                                  ],
                                ),
                              );
                            }).toList(),
                            onChanged: (value) {
                              setState(() {
                                selectedGender = value ?? '';
                              });
                            },
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: bloodTypeController.text.isNotEmpty
                          ? bloodTypeController.text
                          : null,
                      decoration: const InputDecoration(
                        labelText: 'Blood Type',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.bloodtype),
                      ),
                      items: PatientOptions.bloodTypes.map((type) {
                        return DropdownMenuItem(
                          value: type,
                          child: Text(type),
                        );
                      }).toList(),
                      onChanged: (value) {
                        bloodTypeController.text = value ?? '';
                      },
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),

                    // Allergies
                    const Text(
                      'Allergies',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: PatientOptions.commonAllergies.map((allergy) {
                        final isSelected = selectedAllergies.contains(allergy);
                        return FilterChip(
                          label: Text(allergy),
                          selected: isSelected,
                          onSelected: (selected) {
                            setState(() {
                              if (selected) {
                                selectedAllergies.add(allergy);
                              } else {
                                selectedAllergies.remove(allergy);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),

                    // Chronic Conditions
                    const Text(
                      'Chronic Conditions',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: PatientOptions.commonConditions.map((condition) {
                        final isSelected = selectedConditions.contains(condition);
                        return FilterChip(
                          label: Text(condition),
                          selected: isSelected,
                          onSelected: (selected) {
                            setState(() {
                              if (selected) {
                                selectedConditions.add(condition);
                              } else {
                                selectedConditions.remove(condition);
                              }
                            });
                          },
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),

                    // Medications and History
                    TextField(
                      controller: medicationsController,
                      decoration: const InputDecoration(
                        labelText: 'Current Medications',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.medication),
                      ),
                      maxLines: 2,
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: historyController,
                      decoration: const InputDecoration(
                        labelText: 'Medical History',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.history),
                      ),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),

                    // Emergency Contact
                    TextField(
                      controller: emergencyContactController,
                      decoration: const InputDecoration(
                        labelText: 'Emergency Contact Name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.emergency),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: emergencyPhoneController,
                      decoration: const InputDecoration(
                        labelText: 'Emergency Phone',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.phone),
                      ),
                      keyboardType: TextInputType.phone,
                    ),
                    const SizedBox(height: 16),
                    const Divider(),
                    const SizedBox(height: 8),

                    // Additional Info
                    TextField(
                      controller: occupationController,
                      decoration: const InputDecoration(
                        labelText: 'Occupation',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.work),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: addressController,
                      decoration: const InputDecoration(
                        labelText: 'Address',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.location_on),
                      ),
                      maxLines: 2,
                    ),
                  ],
                ),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Cancel'),
              ),
              ElevatedButton(
                onPressed: () {
                  final updatedPatient = patient.copyWith(
                    name: nameController.text.trim(),
                    age: int.tryParse(ageController.text) ?? 0,
                    gender: selectedGender,
                    bloodType: bloodTypeController.text.trim(),
                    allergies: selectedAllergies,
                    chronicConditions: selectedConditions,
                    currentMedications: medicationsController.text.trim(),
                    medicalHistory: historyController.text.trim(),
                    emergencyContact: emergencyContactController.text.trim(),
                    emergencyPhone: emergencyPhoneController.text.trim(),
                    address: addressController.text.trim(),
                    occupation: occupationController.text.trim(),
                  );
                  provider.updatePatient(updatedPatient);
                  Navigator.pop(context);

                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Patient information updated!'),
                      backgroundColor: Colors.green,
                      duration: Duration(seconds: 2),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue.shade700,
                  foregroundColor: Colors.white,
                ),
                child: const Text('Save Changes'),
              ),
            ],
          );
        },
      ),
    );
  }

  void _showPatientSummary(BuildContext context) {
    final provider = Provider.of<PatientProvider>(context, listen: false);
    final patient = provider.currentPatient;
    if (patient == null) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Patient Summary'),
        content: SizedBox(
          width: 400,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSummaryRow('Name', patient.name),
                _buildSummaryRow('Age', '${patient.age} (${patient.ageGroup})'),
                _buildSummaryRow('Gender', patient.genderDisplay),
                _buildSummaryRow('Blood Type', patient.bloodTypeDisplay),
                const Divider(),
                _buildSummaryRow(
                  'Allergies',
                  patient.hasAllergies ? patient.allergies.join(', ') : 'None',
                ),
                _buildSummaryRow(
                  'Chronic Conditions',
                  patient.hasChronicConditions
                      ? patient.chronicConditions.join(', ')
                      : 'None',
                ),
                const Divider(),
                _buildSummaryRow(
                  'Medications',
                  patient.currentMedications.isNotEmpty
                      ? patient.currentMedications
                      : 'None',
                ),
                _buildSummaryRow(
                  'Medical History',
                  patient.medicalHistory.isNotEmpty
                      ? patient.medicalHistory
                      : 'None',
                ),
                const Divider(),
                _buildSummaryRow(
                  'Emergency Contact',
                  patient.emergencyContact.isNotEmpty
                      ? patient.emergencyContact
                      : 'Not set',
                ),
                _buildSummaryRow(
                  'Emergency Phone',
                  patient.emergencyPhone.isNotEmpty
                      ? patient.emergencyPhone
                      : 'Not set',
                ),
                const Divider(),
                _buildSummaryRow(
                  'Occupation',
                  patient.occupation.isNotEmpty ? patient.occupation : 'Not set',
                ),
                _buildSummaryRow(
                  'Address',
                  patient.address.isNotEmpty ? patient.address : 'Not set',
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: Colors.grey.shade600,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showExportDialog(BuildContext context) {
    final provider = Provider.of<PatientProvider>(context, listen: false);
    final patient = provider.currentPatient;
    if (patient == null) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Export Patient Data'),
        content: const Text(
          'This would export patient data including personal information, '
              'vital signs history, and symptom tracking to a file.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Export functionality coming soon!'),
                  duration: Duration(seconds: 2),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue.shade700,
              foregroundColor: Colors.white,
            ),
            child: const Text('Export'),
          ),
        ],
      ),
    );
  }

  void _confirmReset(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset Patient Data?'),
        content: const Text(
          'This will clear all patient data including personal information, '
              'vital signs, and symptoms. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              final provider = Provider.of<PatientProvider>(context, listen: false);
              provider.resetPatient();
              Navigator.pop(context);

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Patient data reset'),
                  backgroundColor: Colors.red,
                ),
              );
            },
            child: const Text(
              'Reset',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }

  void _navigateToTab(BuildContext context, int index) {
    // Find the MainScreen and change tab
    final mainScreen = context.findAncestorStateOfType<MainScreenState>();
    if (mainScreen != null) {
      mainScreen.selectTab(index);
    }
  }
}



// Note: The navigation logic will be updated in main.dart