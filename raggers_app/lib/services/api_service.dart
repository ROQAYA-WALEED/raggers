import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:raggers_app/models/patient_models.dart';
import 'package:raggers_app/models/vital_signs_model.dart';
import 'package:raggers_app/models/symptoms_model.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8001';
  static const String queryEndpoint = '/api/v1/query';

  Future<Map<String, dynamic>> sendQuery({
    required String question,
    required Patient patient,
    List<VitalSigns>? vitalsHistory,
    List<Symptom>? symptoms,
  }) async {
    try {
      // Build minimal patient context
      final patientContext = _buildMinimalPatientContext(patient, vitalsHistory, symptoms);

      // Build minimal prompt
      final fullPrompt = _buildMinimalPrompt(question, patientContext);

      final requestBody = {
        'question': fullPrompt,
      };

      print('📤 Sending request to: $baseUrl$queryEndpoint');
      print('📝 Prompt length: ${fullPrompt.length} characters');
      print('📝 Prompt preview: ${fullPrompt.substring(0, fullPrompt.length > 200 ? 200 : fullPrompt.length)}...');

      final response = await http.post(
        Uri.parse('$baseUrl$queryEndpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode(requestBody),
      );

      print('📥 Response status: ${response.statusCode}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('✅ API response received');
        final formatted = _formatResponse(data);
        return formatted;
      } else {
        print('❌ API Error: ${response.statusCode} - ${response.body}');
        throw Exception('API Error: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      print('❌ API Error: $e');
      return _getFallbackResponse(question);
    }
  }

  // MINIMAL patient context - only essential info
  String _buildMinimalPatientContext(Patient patient, List<VitalSigns>? vitalsHistory, List<Symptom>? symptoms) {
    final parts = <String>[];

    // Basic info
    parts.add('${patient.age}yo ${patient.gender}');

    // Blood type (if available)
    if (patient.bloodType.isNotEmpty && patient.bloodType != 'Unknown') {
      parts.add('Blood ${patient.bloodType}');
    }

    // Chronic conditions (if any)
    if (patient.chronicConditions.isNotEmpty) {
      parts.add('Conditions: ${patient.chronicConditions.join(",")}');
    }

    // Allergies (if any)
    if (patient.allergies.isNotEmpty) {
      parts.add('Allergies: ${patient.allergies.join(",")}');
    }

    // Medications (if any)
    if (patient.currentMedications.isNotEmpty) {
      parts.add('Meds: ${patient.currentMedications}');
    }

    // Latest vitals (compact format)
    if (vitalsHistory != null && vitalsHistory.isNotEmpty) {
      final latest = vitalsHistory.first;
      parts.add('Vitals: ${latest.temperature.toStringAsFixed(1)}C ${latest.heartRate}bpm ${latest.systolicBP}/${latest.diastolicBP} O2${latest.oxygenSaturation}%');
    }

    // Active symptoms (compact)
    if (symptoms != null && symptoms.isNotEmpty) {
      final activeSymptoms = symptoms.where((s) => s.isActive).toList();
      if (activeSymptoms.isNotEmpty) {
        final symptomStr = activeSymptoms.map((s) =>
        '${s.name}(${s.severity.label[0]})' // Short: "Fever(M)" instead of "Fever(Moderate)"
        ).join(',');
        parts.add('Symptoms: $symptomStr');
      }
    }

    return parts.join(' | ');
  }

  // MINIMAL prompt
  String _buildMinimalPrompt(String question, String patientContext) {
    final lowerQuestion = question.toLowerCase();

    // For general questions, skip context entirely
    final generalKeywords = ['what is', 'define', 'explain', 'what are', 'how does', 'tell me about'];
    final isGeneralQuestion = generalKeywords.any((kw) => lowerQuestion.contains(kw));

    // If it's a general question and no patient-specific context is needed
    if (isGeneralQuestion && lowerQuestion.contains('malaria')) {
      return question;
    }

    // If no patient context, just send the question
    if (patientContext.isEmpty || patientContext.trim() == '') {
      return question;
    }

    // Minimal format: context | question
    return '${patientContext} | Q: $question';
  }

  // ============ RESPONSE FORMATTING METHODS ============

  Map<String, dynamic> _formatResponse(dynamic data) {
    print('📊 _formatResponse: Processing response type: ${data.runtimeType}');

    // Handle array response (your API sometimes returns this)
    if (data is List && data.isNotEmpty) {
      print('📊 _formatResponse: Processing array response with ${data.length} items');
      return _formatArrayResponse(data);
    }

    // Handle single object response (your API currently returns this)
    if (data is Map<String, dynamic>) {
      print('📊 _formatResponse: Processing single object response');
      print('📊 _formatResponse: Response keys: ${data.keys}');
      return _formatSingleObjectResponse(data);
    }

    // Fallback for unexpected format
    print('⚠️ _formatResponse: Unexpected response format: ${data.runtimeType}');
    return {
      'content': 'Unexpected response format from the server.',
      'recommendation': '',
      'evidence': '',
      'citations': [],
      'confidence': 'insufficient',
      'was_blocked': true,
      'block_reason': 'Invalid response format',
    };
  }

  Map<String, dynamic> _formatSingleObjectResponse(Map<String, dynamic> data) {
    print('📊 _formatSingleObjectResponse: Processing with keys: ${data.keys}');

    String content = '';
    String recommendation = '';
    String evidence = '';
    List<Map<String, dynamic>> citations = [];
    String confidence = 'medium';
    bool wasBlocked = false;
    String blockReason = '';

    // Check for the recommendation field directly (this is the AI's response)
    if (data['recommendation'] != null && data['recommendation'].toString().isNotEmpty) {
      recommendation = data['recommendation'].toString();
      print('📊 _formatSingleObjectResponse: Found recommendation directly');
    }

    // Get evidence
    if (data['evidence'] != null) {
      evidence = data['evidence'].toString();
    }

    // Get citation
    if (data['citation'] != null) {
      final citationData = data['citation'];
      if (citationData is String && citationData.isNotEmpty && citationData != '[Page N/A]') {
        citations = [
          {
            'id': 'cit_${DateTime.now().millisecondsSinceEpoch}',
            'title': citationData,
            'source': 'Medical Reference',
          }
        ];
      } else if (citationData is List) {
        citations = citationData.map((c) {
          if (c is Map) {
            return Map<String, dynamic>.from(c);
          } else if (c is String) {
            return {
              'id': 'cit_${DateTime.now().millisecondsSinceEpoch}',
              'title': c,
              'source': 'Medical Reference',
            };
          }
          return {
            'id': 'cit_${DateTime.now().millisecondsSinceEpoch}',
            'title': c.toString(),
            'source': 'Medical Reference',
          };
        }).toList();
      }
    }

    // Get confidence
    if (data['confidence'] != null) {
      confidence = data['confidence'].toString();
    }

    // Check for guardrail_metrics
    if (data['guardrail_metrics'] != null) {
      final guardrail = data['guardrail_metrics'];
      print('📊 _formatSingleObjectResponse: Found guardrail_metrics');
      wasBlocked = guardrail['was_blocked'] ?? false;
      blockReason = guardrail['reason'] ?? '';

      if (wasBlocked) {
        if (guardrail['answer'] != null && guardrail['answer'].toString().isNotEmpty) {
          recommendation = guardrail['answer'].toString();
        }
        confidence = 'insufficient';
        print('📊 _formatSingleObjectResponse: Response was blocked');
      }
    }

    // Set content to the recommendation
    content = recommendation;

    // If content is empty, try other fields
    if (content.isEmpty) {
      print('📊 _formatSingleObjectResponse: Content is empty, trying other keys...');

      if (data['answer'] != null && data['answer'].toString().isNotEmpty) {
        content = data['answer'].toString();
      } else if (data['response'] != null && data['response'].toString().isNotEmpty) {
        content = data['response'].toString();
      } else if (data['message'] != null && data['message'].toString().isNotEmpty) {
        content = data['message'].toString();
      } else if (data['content'] != null && data['content'].toString().isNotEmpty) {
        content = data['content'].toString();
      }
    }

    // If still empty, use a fallback
    if (content.isEmpty) {
      content = 'Received response but could not extract content.';
      print('⚠️ No content found in response');
    }

    return {
      'content': content,
      'recommendation': recommendation.isNotEmpty ? recommendation : content,
      'evidence': evidence,
      'citations': citations,
      'confidence': confidence,
      'was_blocked': wasBlocked,
      'block_reason': wasBlocked ? blockReason : '',
    };
  }

  Map<String, dynamic> _formatArrayResponse(List<dynamic> data) {
    print('📊 _formatArrayResponse: Processing ${data.length} items');

    String content = '';
    String recommendation = '';
    String evidence = '';
    List<Map<String, dynamic>> citations = [];
    String confidence = 'medium';
    bool wasBlocked = false;
    String blockReason = '';

    for (var item in data) {
      // Check for LLM response
      if (item['LLM response'] != null) {
        final llmResponse = item['LLM response'];
        recommendation = llmResponse['Recommendation'] ??
            llmResponse['Recomendation'] ??
            llmResponse['answer'] ?? '';
        evidence = llmResponse['Evidence'] ?? '';

        final citationData = llmResponse['Citation'] ?? [];
        if (citationData is String && citationData.isNotEmpty && citationData != '[Page N/A]') {
          citations = [
            {
              'id': 'cit_${DateTime.now().millisecondsSinceEpoch}',
              'title': citationData,
              'source': 'Medical Reference',
            }
          ];
        } else if (citationData is List) {
          citations = citationData.map((c) {
            if (c is Map) {
              return Map<String, dynamic>.from(c);
            } else if (c is String) {
              return {
                'id': 'cit_${DateTime.now().millisecondsSinceEpoch}',
                'title': c,
                'source': 'Medical Reference',
              };
            }
            return {
              'id': 'cit_${DateTime.now().millisecondsSinceEpoch}',
              'title': c.toString(),
              'source': 'Medical Reference',
            };
          }).toList();
        }

        confidence = llmResponse['Confidence'] ?? 'medium';
        content = recommendation;
      }

      if (item['Guardrail metrics'] != null) {
        final guardrail = item['Guardrail metrics'];
        wasBlocked = guardrail['was_blocked'] ?? false;
        blockReason = guardrail['reason'] ?? '';

        if (wasBlocked) {
          content = guardrail['answer'] ??
              'I am sorry, but I can only answer questions based on the provided documents.';
          confidence = 'insufficient';
          recommendation = '';
          evidence = '';
          citations = [];
        }
      }
    }

    if (content.isEmpty) {
      content = 'I received a response but could not parse it properly. Please try again.';
    }

    return {
      'content': content,
      'recommendation': recommendation.isNotEmpty ? recommendation : content,
      'evidence': evidence,
      'citations': citations,
      'confidence': confidence,
      'was_blocked': wasBlocked,
      'block_reason': wasBlocked ? blockReason : '',
    };
  }

  // ============ FALLBACK RESPONSE ============
  Map<String, dynamic> _getFallbackResponse(String question) {
    return {
      'content': 'I apologize, but I\'m having trouble connecting to the medical knowledge base. '
          'Please check your connection and try again.',
      'recommendation': '',
      'evidence': '',
      'citations': [],
      'confidence': 'insufficient',
      'was_blocked': true,
      'block_reason': 'Connection error',
    };
  }

  // ============ HEALTH CHECK ============
  Future<bool> checkApiAvailability() async {
    try {
      final testRequest = {
        'question': 'Is the API available?',
      };

      final response = await http.post(
        Uri.parse('$baseUrl$queryEndpoint'),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: jsonEncode(testRequest),
      );

      return response.statusCode == 200;
    } catch (e) {
      print('❌ API availability check failed: $e');
      return false;
    }
  }
}