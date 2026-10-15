import 'package:flutter/material.dart';

import 'screens/login_screen.dart';

void main() {
  runApp(const FieldFaultTrackerApp());
}

class FieldFaultTrackerApp extends StatelessWidget {
  const FieldFaultTrackerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Saha Arıza Kaydı',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF1565C0)),
        inputDecorationTheme: const InputDecorationTheme(
          border: OutlineInputBorder(),
        ),
      ),
      home: const LoginScreen(),
    );
  }
}
