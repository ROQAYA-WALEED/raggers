import 'package:flutter/material.dart';
import 'package:raggers_app/providers/vital_signs_provider.dart';
import 'package:raggers_app/models/vital_signs_model.dart';
import 'package:provider/provider.dart';
import '../widgets/vital_signs_form.dart';

class VitalSignsScreen extends StatelessWidget {
  const VitalSignsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Vital Signs'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              _showHistoryDialog(context);
            },
          ),
        ],
      ),
      body: Consumer<VitalSignsProvider>(
        builder: (context, vitalProvider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Latest Vitals Summary
                if (vitalProvider.latestVitalSigns != null) ...[
                  _buildLatestVitalsCard(vitalProvider.latestVitalSigns!),
                  const SizedBox(height: 16),
                ],

                // Vital Signs Form
                VitalSignsForm(
                  onSubmit: (vitalSigns) {
                    vitalProvider.addVitalSigns(vitalSigns);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: const Text('Vital signs recorded successfully!'),
                        backgroundColor: Colors.green,
                        duration: const Duration(seconds: 2),
                      ),
                    );
                  },
                ),

                const SizedBox(height: 16),

                // Recent Vitals List
                if (vitalProvider.vitalSignsHistory.isNotEmpty) ...[
                  _buildRecentVitalsList(vitalProvider.vitalSignsHistory),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildLatestVitalsCard(VitalSigns vitals) {
    return Card(
      elevation: 2,
      color: vitals.isNormal ? Colors.green.shade50 : Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  vitals.isNormal ? Icons.check_circle : Icons.warning,
                  color: vitals.isNormal ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  vitals.isNormal ? 'Vitals are normal' : 'Abnormal vitals detected',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: vitals.isNormal ? Colors.green.shade700 : Colors.red.shade700,
                  ),
                ),
                const Spacer(),
                Text(
                  'Recorded: ${_formatTime(vitals.timestamp)}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 16,
              runSpacing: 8,
              children: [
                _buildVitalChip('Temp', '${vitals.temperature.toStringAsFixed(1)}°C'),
                _buildVitalChip('HR', '${vitals.heartRate} bpm'),
                _buildVitalChip('RR', '${vitals.respiratoryRate}/min'),
                _buildVitalChip('BP', '${vitals.systolicBP}/${vitals.diastolicBP}'),
                _buildVitalChip('O2', '${vitals.oxygenSaturation}%'),
                _buildVitalChip('BMI', '${_calculateBMI(vitals.weight, vitals.height).toStringAsFixed(1)}'),
              ],
            ),
            if (!vitals.isNormal) ...[
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.shade100,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: vitals.warnings.map((warning) {
                    return Row(
                      children: [
                        const Icon(Icons.warning, color: Colors.red, size: 16),
                        const SizedBox(width: 4),
                        Text(
                          warning,
                          style: const TextStyle(
                            color: Colors.red,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildVitalChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: Text(
        '$label: $value',
        style: const TextStyle(fontSize: 13),
      ),
    );
  }

  Widget _buildRecentVitalsList(List<VitalSigns> history) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.history, color: Colors.blue),
                SizedBox(width: 8),
                Text(
                  'Recent Records',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: history.length > 5 ? 5 : history.length,
              itemBuilder: (context, index) {
                final vitals = history[history.length - 1 - index];
                return ListTile(
                  dense: true,
                  leading: Icon(
                    vitals.isNormal ? Icons.check_circle : Icons.warning,
                    color: vitals.isNormal ? Colors.green : Colors.orange,
                    size: 20,
                  ),
                  title: Text(
                    '${vitals.temperature.toStringAsFixed(1)}°C | ${vitals.heartRate} bpm | ${vitals.systolicBP}/${vitals.diastolicBP}',
                    style: const TextStyle(fontSize: 14),
                  ),
                  trailing: Text(
                    _formatTime(vitals.timestamp),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  double _calculateBMI(double weight, double height) {
    // Height in meters
    double heightInMeters = height / 100;
    return weight / (heightInMeters * heightInMeters);
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }

  void _showHistoryDialog(BuildContext context) {
    final provider = Provider.of<VitalSignsProvider>(context, listen: false);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Vital Signs History'),
        content: SizedBox(
          width: double.maxFinite,
          height: 400,
          child: provider.vitalSignsHistory.isEmpty
              ? const Center(child: Text('No vitals recorded yet'))
              : ListView.builder(
            itemCount: provider.vitalSignsHistory.length,
            itemBuilder: (context, index) {
              final vitals = provider.vitalSignsHistory[index];
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 4),
                child: ListTile(
                  leading: Icon(
                    vitals.isNormal ? Icons.check_circle : Icons.warning,
                    color: vitals.isNormal ? Colors.green : Colors.orange,
                  ),
                  title: Text(
                    '${vitals.temperature.toStringAsFixed(1)}°C | ${vitals.heartRate} bpm',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  subtitle: Text(
                    'BP: ${vitals.systolicBP}/${vitals.diastolicBP} | O2: ${vitals.oxygenSaturation}% | BMI: ${_calculateBMI(vitals.weight, vitals.height).toStringAsFixed(1)}',
                  ),
                  trailing: Text(
                    '${vitals.timestamp.day}/${vitals.timestamp.month} ${_formatTime(vitals.timestamp)}',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade600,
                    ),
                  ),
                  isThreeLine: true,
                ),
              );
            },
          ),
        ),
        actions: [
          if (provider.vitalSignsHistory.isNotEmpty)
            TextButton(
              onPressed: () {
                provider.clearHistory();
                Navigator.pop(context);
              },
              child: const Text('Clear All'),
            ),
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}