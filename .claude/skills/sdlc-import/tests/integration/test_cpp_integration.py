#!/usr/bin/env python3
"""
Integration tests for C++ project analysis.

Tests the full sdlc-import workflow on a sample C++/CMake project.
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
def cpp_project():
    """Create a minimal C++/CMake project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create CMakeLists.txt
        create_file(
            project_path / "CMakeLists.txt",
            """cmake_minimum_required(VERSION 3.10)
project(MyApp)

# Find Boost
find_package(Boost REQUIRED COMPONENTS system filesystem)

# Add executable
add_executable(myapp src/main.cpp src/utils.cpp)
target_link_libraries(myapp PRIVATE Boost::system Boost::filesystem)

# Add tests
add_executable(tests test/test_main.cpp)
target_link_libraries(tests PRIVATE Boost::system)
"""
        )

        # Create source files
        create_file(
            project_path / "src/main.cpp",
            """#include <iostream>
#include <boost/filesystem.hpp>

int main() {
    boost::filesystem::path p(".");
    std::cout << "Current path: " << p << std::endl;
    return 0;
}
"""
        )

        create_file(
            project_path / "src/utils.cpp",
            """#include "utils.h"
#include <string>

std::string get_version() {
    return "1.0.0";
}
"""
        )

        create_file(
            project_path / "src/utils.h",
            """#pragma once
#include <string>

std::string get_version();
"""
        )

        create_file(
            project_path / "test/test_main.cpp",
            """#include "utils.h"
#include <cassert>

int main() {
    assert(get_version() == "1.0.0");
    return 0;
}
"""
        )

        # Create Conan file
        create_file(
            project_path / "conanfile.txt",
            """[requires]
boost/1.80.0

[generators]
cmake
"""
        )

        create_file(
            project_path / "README.md",
            """# My C++ Project

C++ project using CMake and Boost.
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


class TestCppIntegration:
    """Integration tests for C++ project analysis"""

    def test_analyze_basic_structure(self, cpp_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(cpp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify basic structure
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result

        # Verify project path
        assert result["project_path"] == str(cpp_project)

    def test_language_detection_cpp(self, cpp_project):
        """Test C++ language detection"""
        analyzer = ProjectAnalyzer(str(cpp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify language detection
        assert "language_analysis" in result
        lang_analysis = result["language_analysis"]

        assert "primary_language" in lang_analysis
        assert lang_analysis["primary_language"] == "cpp"

        assert "languages" in lang_analysis
        assert "cpp" in lang_analysis["languages"]
        assert lang_analysis["languages"]["cpp"]["percentage"] > 50

    def test_cmake_detection(self, cpp_project):
        """Test CMake framework detection"""
        analyzer = ProjectAnalyzer(str(cpp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify framework detection
        assert "language_analysis" in result
        frameworks = result["language_analysis"]["frameworks"]

        # CMake should be detected as backend framework
        assert "backend" in frameworks
        backend_frameworks = [f.lower() for f in frameworks["backend"]]
        assert "cmake" in backend_frameworks

    def test_conan_detection(self, cpp_project):
        """Test Conan package manager detection"""
        analyzer = ProjectAnalyzer(str(cpp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify Conan detection
        frameworks = result["language_analysis"]["frameworks"]
        backend_frameworks = [f.lower() for f in frameworks["backend"]]
        assert "conan" in backend_frameworks

    def test_boost_detection(self, cpp_project):
        """Test Boost library detection"""
        analyzer = ProjectAnalyzer(str(cpp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify Boost detection
        frameworks = result["language_analysis"]["frameworks"]
        backend_frameworks = [f.lower() for f in frameworks["backend"]]
        assert "boost" in backend_frameworks

    def test_file_count_cpp(self, cpp_project):
        """Test that C++ files are counted correctly"""
        analyzer = ProjectAnalyzer(str(cpp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify scan results
        scan = result["scan"]
        files_by_ext = scan["files_by_extension"]

        # Should detect .cpp files
        assert ".cpp" in files_by_ext
        assert files_by_ext[".cpp"]["count"] >= 3

        # Should detect .h files
        assert ".h" in files_by_ext
        assert files_by_ext[".h"]["count"] >= 1

    def test_lsp_plugin_cpp(self, cpp_project):
        """Test that clangd LSP plugin is identified"""
        analyzer = ProjectAnalyzer(str(cpp_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify LSP analysis
        lsp_analysis = result["language_analysis"].get("lsp_analysis", {})

        # clangd should be identified for C++
        if "cpp" in lsp_analysis:
            assert lsp_analysis["cpp"]["plugin"] == "clangd-lsp"
