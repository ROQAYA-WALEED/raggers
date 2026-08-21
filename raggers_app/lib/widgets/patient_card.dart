import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:raggers_app/models/patient_models.dart';
import '../providers/patient_provider.dart';

class PatientCard extends StatelessWidget {
  final VoidCallback? onEdit;

  const PatientCard({
    super.key,
    this.onEdit,
  });

  @override
  Widget build(BuildContext context) {
    return Consumer<PatientProvider>(
      builder: (context, patientProvider, child) {
        final patient = patientProvider.currentPatient;

        if (patient == null) {
          return const Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Center(
                child: Text('No patient data available'),
              ),
            ),
          );
        }

        return _buildCardContent(context, patient);
      },
    );
  }

  Widget _buildCardContent(BuildContext context, Patient patient) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _getGenderColor(patient.gender).withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _getGenderIcon(patient.gender),
                    size: 32,
                    color: _getGenderColor(patient.gender),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        patient.name,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Row(
                        children: [
                          Text(
                            '${patient.age} years',
                            style: TextStyle(
                              color: Colors.grey.shade600,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.blue.shade50,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              patient.ageGroup,
                              style: TextStyle(
                                fontSize: 11,
                                color: Colors.blue.shade700,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                if (onEdit != null)
                  IconButton(
                    icon: const Icon(Icons.edit),
                    onPressed: onEdit,
                    tooltip: 'Edit Patient',
                  ),
              ],
            ),
            const SizedBox(height: 12),
            const Divider(),
            const SizedBox(height: 12),

            // Quick info chips
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildInfoChip(
                  _getGenderIcon(patient.gender),
                  patient.genderDisplay,
                  _getGenderColor(patient.gender),
                ),
                _buildInfoChip(
                  Icons.bloodtype,
                  patient.bloodTypeDisplay,
                  Colors.red,
                ),
                if (patient.hasAllergies)
                  _buildInfoChip(
                    Icons.warning,
                    '${patient.allergies.length} allergies',
                    Colors.orange,
                  ),
                if (patient.hasChronicConditions)
                  _buildInfoChip(
                    Icons.medical_information,
                    '${patient.chronicConditions.length} conditions',
                    Colors.purple,
                  ),
                _buildInfoChip(
                  Icons.work,
                  patient.occupation.isNotEmpty ? patient.occupation : 'N/A',
                  Colors.green,
                ),
                if (patient.emergencyContact.isNotEmpty)
                  _buildInfoChip(
                    Icons.emergency,
                    patient.emergencyContact,
                    Colors.red,
                  ),
              ],
            ),

            // Medical summary
            if (patient.medicalHistory.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.history, size: 16, color: Colors.grey.shade600),
                        const SizedBox(width: 4),
                        Text(
                          'Medical History',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.grey.shade700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      patient.medicalHistory,
                      style: TextStyle(
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),
            ],

            // Current medications
            if (patient.currentMedications.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.medication, size: 16, color: Colors.blue.shade700),
                        const SizedBox(width: 4),
                        Text(
                          'Current Medications',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.blue.shade700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      patient.currentMedications,
                      style: TextStyle(
                        color: Colors.blue.shade700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  // Helper method to get gender-specific icon
  IconData _getGenderIcon(String gender) {
    final lowerGender = gender.toLowerCase();
    if (lowerGender == 'male' || lowerGender == 'm') {
      return Icons.male;
    } else if (lowerGender == 'female' || lowerGender == 'f') {
      return Icons.female;
    } else if (lowerGender.contains('non-binary') || lowerGender.contains('nonbinary')) {
      return Icons.transgender;
    } else {
      return Icons.person_outline;
    }
  }

  // Helper method to get gender-specific color
  Color _getGenderColor(String gender) {
    final lowerGender = gender.toLowerCase();
    if (lowerGender == 'male' || lowerGender == 'm') {
      return Colors.blue;
    } else if (lowerGender == 'female' || lowerGender == 'f') {
      return Colors.pink;
    } else if (lowerGender.contains('non-binary') || lowerGender.contains('nonbinary')) {
      return Colors.purple;
    } else {
      return Colors.grey;
    }
  }

  Widget _buildInfoChip(IconData icon, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}