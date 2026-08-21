import 'package:flutter/material.dart';
import 'package:raggers_app/models/symptoms_model.dart';

class SymptomChecker extends StatefulWidget {
  final List<Symptom> symptoms;
  final Function(List<Symptom>) onSymptomsChanged;

  const SymptomChecker({
    super.key,
    required this.symptoms,
    required this.onSymptomsChanged,
  });

  @override
  State<SymptomChecker> createState() => _SymptomCheckerState();
}

class _SymptomCheckerState extends State<SymptomChecker> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';
  Severity? _selectedSeverityFilter;
  bool _showOnlyActive = false;

  List<String> get _allSymptoms => [
    ...CommonSymptoms.malariaSymptoms,
    ...CommonSymptoms.generalSymptoms,
  ];

  List<String> get _filteredSymptoms {
    final all = _allSymptoms;
    final existing = widget.symptoms.map((s) => s.name).toSet();
    final available = all.where((s) => !existing.contains(s)).toList();

    var filtered = available;
    if (_searchQuery.isNotEmpty) {
      filtered = filtered.where((s) =>
          s.toLowerCase().contains(_searchQuery.toLowerCase())
      ).toList();
    }
    return filtered;
  }

  List<Symptom> get _displayedSymptoms {
    var displayed = List<Symptom>.from(widget.symptoms);
    if (_showOnlyActive) {
      displayed = displayed.where((s) => s.isActive).toList();
    }
    if (_selectedSeverityFilter != null) {
      displayed = displayed.where((s) =>
      s.severity == _selectedSeverityFilter
      ).toList();
    }
    // Sort by severity (critical first)
    displayed.sort((a, b) {
      final severityOrder = {
        Severity.critical: 0,
        Severity.severe: 1,
        Severity.moderate: 2,
        Severity.mild: 3,
      };
      return severityOrder[a.severity]!.compareTo(severityOrder[b.severity]!);
    });
    return displayed;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Search and add section
        Card(
          elevation: 0,
          color: Colors.grey.shade50,
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              children: [
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: 'Search symptoms...',
                          prefixIcon: const Icon(Icons.search),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12),
                        ),
                        onChanged: (value) {
                          setState(() {
                            _searchQuery = value;
                          });
                        },
                      ),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: () {
                        if (_searchQuery.isNotEmpty) {
                          _addSymptom(_searchQuery);
                          _searchController.clear();
                          setState(() {
                            _searchQuery = '';
                          });
                        }
                      },
                      icon: const Icon(Icons.add),
                      label: const Text('Add'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blue.shade700,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                // Quick add chips
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: CommonSymptoms.malariaSymptoms.take(8).map((symptom) {
                    final exists = widget.symptoms.any((s) => s.name == symptom);
                    return ActionChip(
                      label: Text(symptom),
                      onPressed: exists ? null : () => _addSymptom(symptom),
                      backgroundColor: exists ? Colors.grey.shade300 : Colors.blue.shade50,
                      disabledColor: Colors.grey.shade300,
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        // Filter controls
        Row(
          children: [
            const Text(
              'Filters:',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(width: 8),
            FilterChip(
              label: const Text('Active'),
              selected: _showOnlyActive,
              onSelected: (selected) {
                setState(() {
                  _showOnlyActive = selected;
                });
              },
            ),
            const SizedBox(width: 8),
            DropdownButton<Severity>(
              value: _selectedSeverityFilter,
              hint: const Text('Severity'),
              items: [
                const DropdownMenuItem(
                  value: null,
                  child: Text('All'),
                ),
                ...Severity.values.map((severity) {
                  return DropdownMenuItem(
                    value: severity,
                    child: Row(
                      children: [
                        Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: severity.color,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(severity.label),
                      ],
                    ),
                  );
                }),
              ],
              onChanged: (value) {
                setState(() {
                  _selectedSeverityFilter = value;
                });
              },
            ),
            const Spacer(),
            Text(
              '${_displayedSymptoms.length} symptoms',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 12,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Symptoms list
        if (_displayedSymptoms.isEmpty)
          Container(
            padding: const EdgeInsets.all(40),
            alignment: Alignment.center,
            child: Column(
              children: [
                Icon(
                  Icons.medical_information,
                  size: 48,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 8),
                Text(
                  'No symptoms recorded',
                  style: TextStyle(
                    color: Colors.grey.shade600,
                    fontSize: 16,
                  ),
                ),
                Text(
                  'Search and add symptoms above',
                  style: TextStyle(
                    color: Colors.grey.shade400,
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          )
        else
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _displayedSymptoms.length,
            itemBuilder: (context, index) {
              final symptom = _displayedSymptoms[index];
              return _buildSymptomCard(symptom);
            },
          ),
      ],
    );
  }

  Widget _buildSymptomCard(Symptom symptom) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: symptom.isActive ? symptom.severity.color : Colors.grey,
            shape: BoxShape.circle,
          ),
        ),
        title: Text(
          symptom.name,
          style: TextStyle(
            decoration: symptom.isActive ? null : TextDecoration.lineThrough,
            color: symptom.isActive ? Colors.black : Colors.grey,
          ),
        ),
        subtitle: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: symptom.severity.color.withOpacity(0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                symptom.severity.label,
                style: TextStyle(
                  fontSize: 11,
                  color: symptom.severity.color,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 8),
            Text(
              '${symptom.duration}',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey.shade600,
              ),
            ),
            if (!symptom.isActive) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.grey.shade200,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text(
                  'Resolved',
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey,
                  ),
                ),
              ),
            ],
          ],
        ),
        isThreeLine: false,
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (symptom.isActive)
              IconButton(
                icon: const Icon(Icons.check_circle_outline, color: Colors.green),
                onPressed: () => _resolveSymptom(symptom.id),
                tooltip: 'Mark as resolved',
                iconSize: 20,
              ),
            IconButton(
              icon: const Icon(Icons.edit, color: Colors.blue),
              onPressed: () => _showEditSymptomDialog(symptom),
              tooltip: 'Edit',
              iconSize: 20,
            ),
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: () => _removeSymptom(symptom.id),
              tooltip: 'Remove',
              iconSize: 20,
            ),
          ],
        ),
        onTap: () => _showSymptomDetails(symptom),
      ),
    );
  }

  void _addSymptom(String name) {
    final newSymptom = Symptom(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: name.trim(),
      severity: Severity.moderate,
      onsetDate: DateTime.now(),
      duration: 'Just started',
    );
    final updatedSymptoms = List<Symptom>.from(widget.symptoms)..add(newSymptom);
    widget.onSymptomsChanged(updatedSymptoms);
    setState(() {});
  }

  void _removeSymptom(String id) {
    final updatedSymptoms = List<Symptom>.from(widget.symptoms)
      ..removeWhere((s) => s.id == id);
    widget.onSymptomsChanged(updatedSymptoms);
    setState(() {});
  }

  void _resolveSymptom(String id) {
    final updatedSymptoms = List<Symptom>.from(widget.symptoms);
    final index = updatedSymptoms.indexWhere((s) => s.id == id);
    if (index != -1) {
      updatedSymptoms[index] = updatedSymptoms[index].copyWith(isActive: false);
      widget.onSymptomsChanged(updatedSymptoms);
      setState(() {});
    }
  }

  void _showEditSymptomDialog(Symptom symptom) {
    final nameController = TextEditingController(text: symptom.name);
    final durationController = TextEditingController(text: symptom.duration);
    final descriptionController = TextEditingController(text: symptom.description ?? '');
    Severity selectedSeverity = symptom.severity;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Symptom'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  labelText: 'Symptom Name',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<Severity>(
                value: selectedSeverity,
                decoration: const InputDecoration(
                  labelText: 'Severity',
                  border: OutlineInputBorder(),
                ),
                items: Severity.values.map((severity) {
                  return DropdownMenuItem(
                    value: severity,
                    child: Row(
                      children: [
                        Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: severity.color,
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(severity.label),
                      ],
                    ),
                  );
                }).toList(),
                onChanged: (value) {
                  if (value != null) {
                    selectedSeverity = value;
                  }
                },
              ),
              const SizedBox(height: 12),
              TextField(
                controller: durationController,
                decoration: const InputDecoration(
                  labelText: 'Duration (e.g., 2 days, 1 week)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description (optional)',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final updatedSymptom = symptom.copyWith(
                name: nameController.text.trim(),
                severity: selectedSeverity,
                duration: durationController.text.trim(),
                description: descriptionController.text.trim().isNotEmpty
                    ? descriptionController.text.trim()
                    : null,
              );
              final updatedSymptoms = List<Symptom>.from(widget.symptoms);
              final index = updatedSymptoms.indexWhere((s) => s.id == symptom.id);
              if (index != -1) {
                updatedSymptoms[index] = updatedSymptom;
                widget.onSymptomsChanged(updatedSymptoms);
                setState(() {});
              }
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue.shade700,
              foregroundColor: Colors.white,
            ),
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showSymptomDetails(Symptom symptom) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(symptom.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailRow('Severity', symptom.severity.label, symptom.severity.color),
            const SizedBox(height: 8),
            _buildDetailRow('Status', symptom.isActive ? 'Active' : 'Resolved',
                symptom.isActive ? Colors.green : Colors.grey),
            const SizedBox(height: 8),
            _buildDetailRow('Onset', _formatDate(symptom.onsetDate), Colors.blue),
            const SizedBox(height: 8),
            _buildDetailRow('Duration', symptom.duration, Colors.orange),
            if (symptom.description != null) ...[
              const SizedBox(height: 8),
              const Text(
                'Description:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(symptom.description!),
            ],
            if (symptom.triggers.isNotEmpty) ...[
              const SizedBox(height: 8),
              const Text(
                'Triggers:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Wrap(
                spacing: 4,
                children: symptom.triggers.map((t) => Chip(label: Text(t))).toList(),
              ),
            ],
          ],
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

  Widget _buildDetailRow(String label, String value, Color color) {
    return Row(
      children: [
        Text(
          '$label: ',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          decoration: BoxDecoration(
            color: color.withOpacity(0.2),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(value),
        ),
      ],
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'Today at ${_formatTime(date)}';
    } else if (difference.inDays == 1) {
      return 'Yesterday at ${_formatTime(date)}';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else if (difference.inDays < 30) {
      return '${(difference.inDays / 7).floor()} weeks ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}