class ApiConfig {
  static const String baseUrl = 'http://localhost:8000';
  static const Duration timeout = Duration(seconds: 30);
  static const int maxRetries = 3;

  // Endpoints
  static const String queryEndpoint = '/query';
  static const String healthEndpoint = '/health';
}