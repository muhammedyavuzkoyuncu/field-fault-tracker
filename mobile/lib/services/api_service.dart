import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'https://field-fault-tracker.onrender.com';

  static String? accessToken;

  static Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (accessToken != null) 'Authorization': 'Bearer $accessToken',
  };

  static Future<List<dynamic>> getList(String endpoint) async {
    final response = await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: _headers,
    );

    if (response.statusCode != 200) {
      throw Exception(
        'İstek başarısız (${response.statusCode}): ${response.body}',
      );
    }

    return jsonDecode(response.body) as List<dynamic>;
  }

  static Future<Map<String, dynamic>> post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: _headers,
      body: jsonEncode(body),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      String message = 'İşlem başarısız.';

      try {
        final data = jsonDecode(response.body);
        message = data['detail'] ?? data['message'] ?? message;
      } catch (_) {}

      throw Exception(message);
    }

    return jsonDecode(response.body) as Map<String, dynamic>;
  }
}