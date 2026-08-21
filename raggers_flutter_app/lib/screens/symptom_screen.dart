import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:raggers_app/models/symptoms_model.dart';
import 'package:raggers_app/providers/symproms_provider.dart';
import 'package:raggers_app/widgets/symprom_checker.dart';

class SymptomsScreen extends StatelessWidget {
  const SymptomsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Symptoms'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.file_copy),
            onPressed: () {
              _showSummaryDialog(context);
            },
            tooltip: 'Summary',
          ),
        ],
      ),
      body: Consumer<SymptomsProvider>(
        builder: (context, symptomsProvider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                // Symptom summary banner
                _buildSummaryBanner(symptomsProvider),
                const SizedBox(height: 16),

                // Symptom checker
                Card(
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: SymptomChecker(
                      symptoms: symptomsProvider.symptoms,
                      onSymptomsChanged: (newSymptoms) {
                        // Clear and re-add all symptoms
                        symptomsProvider.clearAllSymptoms();
                        for (final symptom in newSymptoms) {
                          symptomsProvider.addSymptom(symptom);
                        }
                      },
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

  Widget _buildSummaryBanner(SymptomsProvider provider) {
    final activeCount = provider.activeSymptoms.length;
    final severeCount = provider.getSymptomsBySeverity(Severity.severe).length +
        provider.getSymptomsBySeverity(Severity.critical).length;

    return Card(
      color: activeCount > 0 ? Colors.blue.shade50 : Colors.grey.shade50,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildSummaryItem(
              'Active',
              '$activeCount',
              activeCount > 0 ? Colors.blue : Colors.grey,
              Icons.favorite,
            ),
            Container(
              width: 1,
              height: 30,
              color: Colors.grey.shade300,
            ),
            _buildSummaryItem(
              'Severe',
              '$severeCount',
              severeCount > 0 ? Colors.red : Colors.grey,
              Icons.warning,
            ),
            Container(
              width: 1,
              height: 30,
              color: Colors.grey.shade300,
            ),
            _buildSummaryItem(
              'Resolved',
              '${provider.resolvedSymptoms.length}',
              provider.resolvedSymptoms.isNotEmpty ? Colors.green : Colors.grey,
              Icons.check_circle,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value, Color color, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: color, size: 20),
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
    );
  }

  void _showSummaryDialog(BuildContext context) {
    final provider = Provider.of<SymptomsProvider>(context, listen: false);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Symptom Summary'),
        content: SizedBox(
          width: double.maxFinite,
          height: 300,
          child: provider.symptoms.isEmpty
              ? const Center(
            child: Text('No symptoms recorded yet'),
          )
              : ListView(
            children: [
              // Active symptoms section
              if (provider.activeSymptoms.isNotEmpty) ...[
                const Text(
                  'Active Symptoms',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                ),
                ...provider.activeSymptoms.map((s) =>
                    ListTile(
                      dense: true,
                      leading: Container(
                        width: 10,
                        height: 10,
                        decoration: BoxDecoration(
                          color: s.severity.color,
                          shape: BoxShape.circle,
                        ),
                      ),
                      title: Text(s.name),
                      trailing: Text(
                        s.severity.label,
                        style: TextStyle(
                          color: s.severity.color,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ),
                const Divider(),
              ],
              // Resolved symptoms section
              if (provider.resolvedSymptoms.isNotEmpty) ...[
                const Text(
                  'Resolved Symptoms',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                ...provider.resolvedSymptoms.map((s) =>
                    ListTile(
                      dense: true,
                      leading: const Icon(
                        Icons.check_circle,
                        color: Colors.green,
                        size: 16,
                      ),
                      title: Text(
                        s.name,
                        style: const TextStyle(
                          decoration: TextDecoration.lineThrough,
                          color: Colors.grey,
                        ),
                      ),
                      trailing: Text(
                        s.severity.label,
                        style: TextStyle(
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ),
                ),
              ],
            ],
          ),
        ),
        actions: [
          if (provider.symptoms.isNotEmpty)
            TextButton(
              onPressed: () {
                provider.clearAllSymptoms();
                Navigator.pop(context);
              },
              child: const Text(
                'Clear All',
                style: TextStyle(color: Colors.red),
              ),
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