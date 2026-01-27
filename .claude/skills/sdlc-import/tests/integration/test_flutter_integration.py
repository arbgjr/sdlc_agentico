#!/usr/bin/env python3
"""
Integration tests for Flutter/Dart project analysis.

Tests the full sdlc-import workflow on a sample Flutter mobile project.
"""

import sys
import pytest
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from project_analyzer import ProjectAnalyzer


def create_file(path: Path, content: str):
    """Helper to create file with content"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


@pytest.fixture
def flutter_project():
    """Create a minimal Flutter project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create pubspec.yaml
        create_file(
            project_path / "pubspec.yaml",
            """name: my_flutter_app
description: A sample Flutter application

version: 1.0.0+1

environment:
  sdk: ">=3.0.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2
  http: ^1.1.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0
"""
        )

        # Create main.dart
        create_file(
            project_path / "lib/main.dart",
            """import 'package:flutter/material.dart';
import 'package:my_flutter_app/screens/home_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const HomeScreen(),
    );
  }
}
"""
        )

        # Create HomeScreen widget
        create_file(
            project_path / "lib/screens/home_screen.dart",
            """import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Home'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            const Text('You have pushed the button this many times:'),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: 'Increment',
        child: const Icon(Icons.add),
      ),
    );
  }
}
"""
        )

        # Create API service
        create_file(
            project_path / "lib/services/api_service.dart",
            """import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'https://api.example.com';

  Future<Map<String, dynamic>> fetchData() async {
    final response = await http.get(Uri.parse('$baseUrl/data'));

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load data');
    }
  }
}
"""
        )

        # Create test file
        create_file(
            project_path / "test/widget_test.dart",
            """import 'package:flutter_test/flutter_test.dart';
import 'package:my_flutter_app/main.dart';

void main() {
  testWidgets('Counter increments smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('0'), findsOneWidget);
    expect(find.text('1'), findsNothing);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pump();

    expect(find.text('0'), findsNothing);
    expect(find.text('1'), findsOneWidget);
  });
}
"""
        )

        create_file(
            project_path / "README.md",
            """# My Flutter App

A Flutter mobile application.
"""
        )

        # Initialize git (required for analyze())
        import subprocess
        subprocess.run(["git", "init"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(project_path), check=True, capture_output=True)

        yield project_path


class TestFlutterIntegration:
    """Integration tests for Flutter/Dart project analysis"""

    def test_analyze_basic_structure(self, flutter_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(flutter_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify basic structure
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result

    def test_language_detection_dart(self, flutter_project):
        """Test Dart language detection"""
        analyzer = ProjectAnalyzer(str(flutter_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify language detection
        assert "language_analysis" in result
        lang_analysis = result["language_analysis"]

        assert "primary_language" in lang_analysis
        assert lang_analysis["primary_language"] == "dart"

        assert "languages" in lang_analysis
        assert "dart" in lang_analysis["languages"]
        assert lang_analysis["languages"]["dart"]["percentage"] > 50

    def test_flutter_framework_detection(self, flutter_project):
        """Test Flutter framework detection"""
        analyzer = ProjectAnalyzer(str(flutter_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify framework detection
        assert "language_analysis" in result
        frameworks = result["language_analysis"]["frameworks"]

        # Flutter should be detected as mobile framework
        assert "mobile" in frameworks
        mobile_frameworks = [f.lower() for f in frameworks["mobile"]]
        assert "flutter" in mobile_frameworks

    def test_flutter_widgets_detection(self, flutter_project):
        """Test Flutter widgets pattern detection"""
        analyzer = ProjectAnalyzer(str(flutter_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify Flutter widgets detected
        frameworks = result["language_analysis"]["frameworks"]
        mobile_frameworks = [f.lower() for f in frameworks["mobile"]]

        # Should detect Flutter widgets pattern
        assert "flutter widgets" in mobile_frameworks or "flutter" in mobile_frameworks

    def test_file_count_dart(self, flutter_project):
        """Test that Dart files are counted correctly"""
        analyzer = ProjectAnalyzer(str(flutter_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify scan results
        scan = result["scan"]
        files_by_ext = scan["files_by_extension"]

        # Should detect .dart files
        assert ".dart" in files_by_ext
        assert files_by_ext[".dart"]["count"] >= 4

    def test_lsp_plugin_dart(self, flutter_project):
        """Test that dart LSP plugin is identified"""
        analyzer = ProjectAnalyzer(str(flutter_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify LSP analysis
        lsp_analysis = result["language_analysis"].get("lsp_analysis", {})

        # dart-lsp should be identified for Dart
        if "dart" in lsp_analysis:
            assert lsp_analysis["dart"]["plugin"] == "dart-lsp"
