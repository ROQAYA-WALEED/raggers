import 'package:flutter/material.dart';
import 'package:raggers_app/models/vital_signs_model.dart';

class VitalSignsForm extends StatefulWidget {
  final Function(VitalSigns) onSubmit;

  const VitalSignsForm({super.key, required this.onSubmit});

  @override
  State<VitalSignsForm> createState() => _VitalSignsFormState();
}

class _VitalSignsFormState extends State<VitalSignsForm> {
  final _formKey = GlobalKey<FormState>();

  // Controllers for vital signs
  final _temperatureController = TextEditingController();
  final _heartRateController = TextEditingController();
  final _respiratoryRateController = TextEditingController();
  final _systolicBPController = TextEditingController();
  final _diastolicBPController = TextEditingController();
  final _oxygenSaturationController = TextEditingController();
  final _weightController = TextEditingController();
  final _heightController = TextEditingController();
  final _notesController = TextEditingController();

  @override
  void dispose() {
    _temperatureController.dispose();
    _heartRateController.dispose();
    _respiratoryRateController.dispose();
    _systolicBPController.dispose();
    _diastolicBPController.dispose();
    _oxygenSaturationController.dispose();
    _weightController.dispose();
    _heightController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.medical_services, color: Colors.blue),
                  const SizedBox(width: 8),
                  const Text(
                    'Record Vital Signs',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const Spacer(),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.blue.shade50,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Patient: Demo Patient',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.blue.shade700,
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              const Divider(),
              const SizedBox(height: 16),

              // Temperature and Heart Rate
              Row(
                children: [
                  Expanded(
                    child: _buildTextField(
                      controller: _temperatureController,
                      label: 'Temperature (°C)',
                      icon: Icons.thermostat,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final temp = double.tryParse(value);
                        if (temp == null || temp < 30 || temp > 45) {
                          return 'Invalid (30-45°C)';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildTextField(
                      controller: _heartRateController,
                      label: 'Heart Rate (bpm)',
                      icon: Icons.favorite,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final hr = int.tryParse(value);
                        if (hr == null || hr < 30 || hr > 220) {
                          return 'Invalid (30-220)';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Respiratory Rate and Oxygen Saturation
              Row(
                children: [
                  Expanded(
                    child: _buildTextField(
                      controller: _respiratoryRateController,
                      label: 'Respiratory Rate',
                      icon: Icons.air,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final rr = int.tryParse(value);
                        if (rr == null || rr < 5 || rr > 50) {
                          return 'Invalid (5-50)';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildTextField(
                      controller: _oxygenSaturationController,
                      label: 'O2 Saturation (%)',
                      icon: Icons.water,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final o2 = double.tryParse(value);
                        if (o2 == null || o2 < 70 || o2 > 100) {
                          return 'Invalid (70-100)';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Blood Pressure
              Row(
                children: [
                  Expanded(
                    child: _buildTextField(
                      controller: _systolicBPController,
                      label: 'Systolic BP',
                      icon: Icons.bloodtype,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final bp = int.tryParse(value);
                        if (bp == null || bp < 70 || bp > 250) {
                          return 'Invalid (70-250)';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildTextField(
                      controller: _diastolicBPController,
                      label: 'Diastolic BP',
                      icon: Icons.bloodtype_outlined,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final bp = int.tryParse(value);
                        if (bp == null || bp < 40 || bp > 180) {
                          return 'Invalid (40-180)';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Weight and Height
              Row(
                children: [
                  Expanded(
                    child: _buildTextField(
                      controller: _weightController,
                      label: 'Weight (kg)',
                      icon: Icons.monitor_weight,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final weight = double.tryParse(value);
                        if (weight == null || weight < 2 || weight > 300) {
                          return 'Invalid (2-300kg)';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildTextField(
                      controller: _heightController,
                      label: 'Height (cm)',
                      icon: Icons.straighten,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'Required';
                        final height = double.tryParse(value);
                        if (height == null || height < 50 || height > 250) {
                          return 'Invalid (50-250cm)';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Notes
              _buildTextField(
                controller: _notesController,
                label: 'Notes (optional)',
                icon: Icons.note,
                maxLines: 2,
                validator: null,
              ),
              const SizedBox(height: 20),

              // Submit Button
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton.icon(
                  onPressed: _submitVitalSigns,
                  icon: const Icon(Icons.save),
                  label: const Text(
                    'Record Vital Signs',
                    style: TextStyle(fontSize: 16),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue.shade700,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    String? Function(String?)? validator,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: Colors.blue.shade700),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.blue.shade700, width: 2),
        ),
      ),
      keyboardType: maxLines > 1 ? TextInputType.multiline : TextInputType.number,
      maxLines: maxLines,
      validator: validator,
    );
  }

  void _submitVitalSigns() {
    if (_formKey.currentState!.validate()) {
      final vitalSigns = VitalSigns(
        timestamp: DateTime.now(),
        temperature: double.parse(_temperatureController.text),
        heartRate: int.parse(_heartRateController.text),
        respiratoryRate: int.parse(_respiratoryRateController.text),
        systolicBP: int.parse(_systolicBPController.text),
        diastolicBP: int.parse(_diastolicBPController.text),
        oxygenSaturation: int.parse(_oxygenSaturationController.text),
        weight: double.parse(_weightController.text),
        height: double.parse(_heightController.text),
        notes: _notesController.text.isNotEmpty ? _notesController.text : null,
      );

      widget.onSubmit(vitalSigns);

      // Clear form after submission
      _formKey.currentState!.reset();
      _temperatureController.clear();
      _heartRateController.clear();
      _respiratoryRateController.clear();
      _systolicBPController.clear();
      _diastolicBPController.clear();
      _oxygenSaturationController.clear();
      _weightController.clear();
      _heightController.clear();
      _notesController.clear();
    }
  }
}