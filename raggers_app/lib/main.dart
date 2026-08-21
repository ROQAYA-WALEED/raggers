import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:raggers_app/models/patient_models.dart';
import 'package:raggers_app/models/vital_signs_model.dart';
import 'screens/chat_screen.dart';
import 'screens/vital_signs_screen.dart';
import 'screens/symptom_screen.dart';
import 'screens/patient_screen.dart';
import 'providers/vital_signs_provider.dart';
import 'providers/symproms_provider.dart';
import 'providers/patient_provider.dart';
import 'providers/chat_provider.dart';  // Add this import
import 'services/database_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize database
  final db = DatabaseService();
  await db.init();

  // Load saved data or create demo data
  await _initializeDemoData(db);

  runApp(const MyApp());
}

Future<void> _initializeDemoData(DatabaseService db) async {
  // Check if we already have data
  if (db.patientCount > 0) {
    print('✅ Data already exists, skipping demo data');
    return;
  }

  print('📝 Creating demo patient data...');

  // Create demo patient
  final patient = Patient(
    id: 'PAT-${DateTime.now().millisecondsSinceEpoch}',
    name: 'Demo Patient',
    age: 35,
    gender: 'Male',
    bloodType: 'O+',
    allergies: ['Penicillin'],
    chronicConditions: ['Hypertension'],
    currentMedications: 'Lisinopril 10mg daily',
    medicalHistory: 'No significant history',
    emergencyContact: 'Jane Doe',
    emergencyPhone: '+1 555-0123',
    address: '123 Main St, City, State 12345',
    occupation: 'Software Engineer',
  );
  await db.savePatient(patient);

  // Create demo vitals
  final vitals = VitalSigns(
    timestamp: DateTime.now(),
    temperature: 37.2,
    heartRate: 75,
    respiratoryRate: 16,
    systolicBP: 120,
    diastolicBP: 80,
    oxygenSaturation: 98,
    weight: 70,
    height: 175,
    notes: 'Initial vitals recorded',
  );
  await db.saveVitalSigns(vitals);

  print('✅ Demo data created successfully!');
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => PatientProvider()),
        ChangeNotifierProvider(create: (_) => VitalSignsProvider()),
        ChangeNotifierProvider(create: (_) => SymptomsProvider()),
        ChangeNotifierProvider(create: (_) => ChatProvider()),  // Add this
      ],
      child: MaterialApp(
        title: 'Malaria Assistant',
        theme: ThemeData(
          primarySwatch: Colors.blue,
          useMaterial3: true,
        ),
        home: const MainScreen(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => MainScreenState();
}

class MainScreenState extends State<MainScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [
    const ChatScreen(),
    const VitalSignsScreen(),
    const SymptomsScreen(),
    const PatientScreen(),
  ];

  void selectTab(int index) {
    if (index >= 0 && index < _screens.length) {
      setState(() {
        _selectedIndex = index;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.chat),
            label: 'Chat',
          ),
          NavigationDestination(
            icon: Icon(Icons.medical_services),
            label: 'Vitals',
          ),
          NavigationDestination(
            icon: Icon(Icons.healing),
            label: 'Symptoms',
          ),
          NavigationDestination(
            icon: Icon(Icons.person),
            label: 'Patient',
          ),
        ],
      ),
    );
  }
}