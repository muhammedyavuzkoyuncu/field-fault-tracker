import 'package:flutter/material.dart';

import '../services/api_service.dart';
import 'login_screen.dart';
import 'new_fault_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  void _openNewFaultScreen(BuildContext context) {
    debugPrint('1 - TIKLAMA ALGILANDI');

    Navigator.of(context)
        .push(
          MaterialPageRoute<void>(
            builder: (context) {
              debugPrint('2 - NEW FAULT SCREEN OLUŞTURULUYOR');
              return const NewFaultScreen();
            },
          ),
        )
        .then((_) {
          debugPrint('3 - NEW FAULT SCREEN KAPANDI');
        });
  }

  void _showComingSoon(BuildContext context, String feature) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$feature henüz kullanıma hazır değil.'),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _logout(BuildContext context) {
    ApiService.accessToken = null;

    Navigator.of(context).pushAndRemoveUntil(
      PageRouteBuilder<void>(
        pageBuilder: (context, animation, secondaryAnimation) =>
            const LoginScreen(),
        transitionDuration: Duration.zero,
        reverseTransitionDuration: Duration.zero,
      ),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Saha Arıza Kaydı',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Çıkış Yap',
            onPressed: () => _logout(context),
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),

              const Text(
                'Hoş Geldiniz 👋',
                style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
              ),

              const SizedBox(height: 8),

              Text(
                'Saha arıza yönetim paneli',
                style: TextStyle(color: Colors.grey.shade600, fontSize: 16),
              ),

              const SizedBox(height: 30),

              _buildMenuCard(
                context: context,
                icon: Icons.add_circle_outline,
                title: 'Yeni Arıza Kaydı2',
                subtitle: 'Sahadaki yeni arızayı sisteme kaydet',
                onTap: () => _openNewFaultScreen(context),
              ),

              const SizedBox(height: 14),

              _buildMenuCard(
                context: context,
                icon: Icons.list_alt,
                title: 'Arıza Kayıtları',
                subtitle: 'Mevcut arıza kayıtlarını görüntüle',
                onTap: () => _showComingSoon(context, 'Arıza Kayıtları'),
              ),

              const SizedBox(height: 14),

              _buildMenuCard(
                context: context,
                icon: Icons.precision_manufacturing_outlined,
                title: 'Ekipmanlar',
                subtitle: 'Sistemdeki ekipmanları görüntüle',
                onTap: () => _showComingSoon(context, 'Ekipmanlar'),
              ),

              const SizedBox(height: 14),

              _buildMenuCard(
                context: context,
                icon: Icons.engineering_outlined,
                title: 'Teknisyenler',
                subtitle: 'Teknisyen bilgilerini görüntüle',
                onTap: () => _showComingSoon(context, 'Teknisyenler'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuCard({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      clipBehavior: Clip.antiAlias,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              CircleAvatar(
                radius: 27,
                backgroundColor: Theme.of(context).colorScheme.primaryContainer,
                child: Icon(
                  icon,
                  size: 28,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
              ),

              const SizedBox(width: 16),

              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey.shade600,
                      ),
                    ),
                  ],
                ),
              ),

              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}
