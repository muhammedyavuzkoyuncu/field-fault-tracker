import 'package:flutter/material.dart';

import '../services/api_service.dart';

class NewFaultScreen extends StatefulWidget {
  const NewFaultScreen({super.key});

  @override
  State<NewFaultScreen> createState() => _NewFaultScreenState();
}

class _NewFaultScreenState extends State<NewFaultScreen> {
  List<dynamic> _equipment = [];
  List<dynamic> _categories = [];
  List<dynamic> _technicians = [];

  int? _selectedEquipmentId;
  int? _selectedCategoryId;
  int? _selectedTechnicianId;

  String _selectedPriority = 'ORTA';

  final _titleController = TextEditingController();
  final _descriptionController = TextEditingController();

  bool _isLoading = true;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _loadData() async {
    try {
      final results = await Future.wait([
        ApiService.getList('/equipment'),
        ApiService.getList('/fault-categories'),
        ApiService.getList('/technicians'),
      ]);

      if (!mounted) return;

      setState(() {
        _equipment = results[0];
        _categories = results[1];
        _technicians = results[2];
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        _isLoading = false;
      });

      _showMessage('Veriler yüklenemedi.\n$e', isError: true);
    }
  }

  Future<void> _saveFault() async {
    if (_selectedEquipmentId == null ||
        _selectedCategoryId == null ||
        _selectedTechnicianId == null) {
      _showMessage('Ekipman, kategori ve teknisyen seçiniz.', isError: true);
      return;
    }

    final title = _titleController.text.trim();
    final description = _descriptionController.text.trim();

    if (title.isEmpty) {
      _showMessage('Arıza başlığını giriniz.', isError: true);
      return;
    }

    if (description.isEmpty) {
      _showMessage('Arıza açıklamasını giriniz.', isError: true);
      return;
    }

    setState(() {
      _isSaving = true;
    });

    try {
      final result = await ApiService.post('/faults', {
        'equipment_id': _selectedEquipmentId,
        'category_id': _selectedCategoryId,
        'technician_id': _selectedTechnicianId,
        'title': title,
        'description': description,
        'priority': _selectedPriority,
      });

      if (!mounted) return;

      _showMessage('Arıza başarıyla kaydedildi. ID: ${result['fault_id']}');

      Navigator.pop(context, true);
    } catch (e) {
      if (!mounted) return;

      _showMessage('Arıza kaydedilemedi.\n$e', isError: true);
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  void _showMessage(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Colors.red : Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Yeni Arıza Kaydı',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Text(
                    'Arıza Bilgileri',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                  ),

                  const SizedBox(height: 20),

                  // EKİPMAN
                  DropdownButtonFormField<int>(
                    initialValue: _selectedEquipmentId,
                    decoration: const InputDecoration(
                      labelText: 'Ekipman',
                      prefixIcon: Icon(Icons.precision_manufacturing),
                    ),
                    hint: const Text('Ekipman seçiniz'),
                    items: _equipment.map((item) {
                      return DropdownMenuItem<int>(
                        value: item['id'] as int,
                        child: Text(
                          '${item['equipment_code']} - ${item['name']}',
                        ),
                      );
                    }).toList(),
                    onChanged: _isSaving
                        ? null
                        : (value) {
                            setState(() {
                              _selectedEquipmentId = value;
                            });
                          },
                  ),

                  const SizedBox(height: 16),

                  // KATEGORİ
                  DropdownButtonFormField<int>(
                    initialValue: _selectedCategoryId,
                    decoration: const InputDecoration(
                      labelText: 'Arıza Kategorisi',
                      prefixIcon: Icon(Icons.category_outlined),
                    ),
                    hint: const Text('Kategori seçiniz'),
                    items: _categories.map((item) {
                      return DropdownMenuItem<int>(
                        value: item['id'] as int,
                        child: Text(
                          '${item['category_code']} - ${item['name']}',
                        ),
                      );
                    }).toList(),
                    onChanged: _isSaving
                        ? null
                        : (value) {
                            setState(() {
                              _selectedCategoryId = value;
                            });
                          },
                  ),

                  const SizedBox(height: 16),

                  // TEKNİSYEN
                  DropdownButtonFormField<int>(
                    initialValue: _selectedTechnicianId,
                    decoration: const InputDecoration(
                      labelText: 'Teknisyen',
                      prefixIcon: Icon(Icons.engineering_outlined),
                    ),
                    hint: const Text('Teknisyen seçiniz'),
                    items: _technicians.map((item) {
                      return DropdownMenuItem<int>(
                        value: item['id'] as int,
                        child: Text(item['full_name'].toString()),
                      );
                    }).toList(),
                    onChanged: _isSaving
                        ? null
                        : (value) {
                            setState(() {
                              _selectedTechnicianId = value;
                            });
                          },
                  ),

                  const SizedBox(height: 16),

                  // BAŞLIK
                  TextField(
                    controller: _titleController,
                    enabled: !_isSaving,
                    decoration: const InputDecoration(
                      labelText: 'Arıza Başlığı',
                      hintText: 'Örn: Pompa çalışmıyor',
                      prefixIcon: Icon(Icons.title),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // AÇIKLAMA
                  TextField(
                    controller: _descriptionController,
                    enabled: !_isSaving,
                    maxLines: 5,
                    decoration: const InputDecoration(
                      labelText: 'Açıklama',
                      hintText: 'Arızayı detaylı şekilde açıklayınız',
                      alignLabelWithHint: true,
                      prefixIcon: Icon(Icons.description_outlined),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // ÖNCELİK
                  DropdownButtonFormField<String>(
                    initialValue: _selectedPriority,
                    decoration: const InputDecoration(
                      labelText: 'Öncelik',
                      prefixIcon: Icon(Icons.priority_high),
                    ),
                    items: const [
                      DropdownMenuItem(value: 'DÜŞÜK', child: Text('Düşük')),
                      DropdownMenuItem(value: 'ORTA', child: Text('Orta')),
                      DropdownMenuItem(value: 'YÜKSEK', child: Text('Yüksek')),
                      DropdownMenuItem(value: 'KRİTİK', child: Text('Kritik')),
                    ],
                    onChanged: _isSaving
                        ? null
                        : (value) {
                            if (value == null) return;

                            setState(() {
                              _selectedPriority = value;
                            });
                          },
                  ),

                  const SizedBox(height: 28),

                  // KAYDET
                  SizedBox(
                    height: 54,
                    child: FilledButton.icon(
                      onPressed: _isSaving ? null : _saveFault,
                      icon: _isSaving
                          ? const SizedBox(
                              width: 22,
                              height: 22,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                color: Colors.white,
                              ),
                            )
                          : const Icon(Icons.save_outlined),
                      label: Text(
                        _isSaving ? 'Kaydediliyor...' : 'Arıza Kaydet',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}
