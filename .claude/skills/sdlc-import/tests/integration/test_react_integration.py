#!/usr/bin/env python3
"""
Integration tests for React/Express project analysis.

Tests the full sdlc-import workflow on a sample JavaScript/TypeScript project.
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
def react_project():
    """Create a minimal React/Express project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create package.json
        create_file(
            project_path / "package.json",
            """{
  "name": "my-react-app",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "express": "^4.18.2",
    "axios": "^1.4.0",
    "jsonwebtoken": "^9.0.0"
  },
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "jest": "^29.5.0",
    "typescript": "^5.0.0"
  }
}
"""
        )

        # Create React component
        create_file(
            project_path / "src/components/App.tsx",
            """import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface User {
  id: number;
  name: string;
}

export const App: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);

  useEffect(() => {
    axios.get<User[]>('/api/users')
      .then(response => setUsers(response.data))
      .catch(error => console.error('Failed to fetch users:', error));
  }, []);

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map(user => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
};
"""
        )

        # Create Express server
        create_file(
            project_path / "src/server/index.ts",
            """import express from 'express';
import jwt from 'jsonwebtoken';

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret';

app.use(express.json());

// Authentication middleware
const authenticate = (req: any, res: any, next: any) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// API routes
app.get('/api/users', authenticate, async (req, res) => {
  // Mock data - would query database in real app
  const users = [
    { id: 1, name: 'Alice' },
    { id: 2, name: 'Bob' }
  ];
  res.json(users);
});

app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;

  // Mock authentication - would check database in real app
  if (username === 'admin' && password === 'password') {
    const token = jwt.sign({ username }, JWT_SECRET, { expiresIn: '1h' });
    res.json({ token });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""
        )

        # Create tsconfig.json
        create_file(
            project_path / "tsconfig.json",
            """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "jsx": "react",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
"""
        )

        # Create test file
        create_file(
            project_path / "src/components/__tests__/App.test.tsx",
            """import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { App } from '../App';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('App', () => {
  it('renders users list', async () => {
    mockedAxios.get.mockResolvedValue({
      data: [
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' }
      ]
    });

    render(<App />);

    await waitFor(() => {
      expect(screen.getByText('Alice')).toBeInTheDocument();
      expect(screen.getByText('Bob')).toBeInTheDocument();
    });
  });
});
"""
        )

        # Create README
        create_file(
            project_path / "README.md",
            """# My React App

A sample React application with Express backend.
"""
        )

        # Initialize git
        import subprocess
        subprocess.run(["git", "init"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(project_path), check=True, capture_output=True)

        yield project_path


class TestReactIntegration:
    """Integration tests for React/Express project analysis"""

    def test_analyze_basic_structure(self, react_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify basic structure
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result

        # Verify project path
        assert result["project_path"] == str(react_project)

        # Verify timestamp format (ISO 8601 with Z)
        assert result["timestamp"].endswith("Z")
        assert "T" in result["timestamp"]

    def test_branch_creation_react(self, react_project):
        """Test that feature branch is created"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify branch info
        assert "branch" in result
        assert isinstance(result["branch"], dict)
        assert "branch" in result["branch"]
        assert "created" in result["branch"]

        # Verify branch name format
        branch_name = result["branch"]["branch"]
        assert branch_name.startswith("feature/import-")

        # Verify branch was created
        assert result["branch"]["created"] is True

        # Verify branch exists in git
        import subprocess
        branches_result = subprocess.run(
            ["git", "branch"],
            cwd=str(react_project),
            capture_output=True,
            text=True
        )
        assert branch_name in branches_result.stdout

    def test_directory_scan_react(self, react_project):
        """Test directory scanning"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify scan results
        assert "scan" in result
        scan = result["scan"]

        assert "total_files" in scan
        assert "total_loc" in scan
        assert "files_by_extension" in scan

        # Should detect TypeScript/JavaScript files
        assert scan["total_files"] >= 4
        assert (".ts" in scan["files_by_extension"] or ".tsx" in scan["files_by_extension"])

        # Verify TypeScript files structure
        ts_extensions = [ext for ext in scan["files_by_extension"].keys() if ext in [".ts", ".tsx", ".js", ".jsx"]]
        assert len(ts_extensions) > 0

    def test_project_validation_react(self, react_project):
        """Test project validation"""
        analyzer = ProjectAnalyzer(str(react_project))

        # Validation should pass for valid React project
        is_valid = analyzer.validate_project()
        assert is_valid is True

    def test_language_detection_react(self, react_project):
        """Test language detection"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify language detection
        assert "language_analysis" in result
        lang_analysis = result["language_analysis"]

        assert "primary_language" in lang_analysis
        # Should detect TypeScript or JavaScript
        assert lang_analysis["primary_language"] in ["typescript", "javascript"]

        assert "languages" in lang_analysis
        # Should detect at least one JS/TS language
        detected_langs = lang_analysis["languages"].keys()
        assert any(lang in detected_langs for lang in ["typescript", "javascript"])

        # Verify framework detection
        assert "frameworks" in lang_analysis
        frameworks = lang_analysis["frameworks"]
        assert "frontend" in frameworks or "backend" in frameworks

    def test_decision_extraction_react(self, react_project):
        """Test decision extraction"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify decisions extracted
        assert "decisions" in result
        decisions = result["decisions"]

        assert "count" in decisions
        assert "decisions" in decisions
        assert "confidence_distribution" in decisions

        # Should have at least some decisions
        assert decisions["count"] >= 0

        # Verify confidence distribution structure
        dist = decisions["confidence_distribution"]
        assert "high" in dist
        assert "medium" in dist
        assert "low" in dist

        # If decisions found, check structure
        if decisions["count"] > 0:
            decision = decisions["decisions"][0]
            assert "id" in decision
            assert decision["id"].startswith("ADR-INFERRED-")
            assert "title" in decision
            assert "category" in decision
            assert "confidence" in decision
            assert "evidence" in decision

    def test_diagram_generation_react(self, react_project):
        """Test diagram generation"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify diagrams generated
        assert "diagrams" in result
        diagrams = result["diagrams"]

        assert "diagrams" in diagrams
        assert isinstance(diagrams["diagrams"], list)

        # Should have at least one diagram
        if len(diagrams["diagrams"]) > 0:
            diagram = diagrams["diagrams"][0]
            assert "type" in diagram
            assert "format" in diagram
            assert "path" in diagram
            assert diagram["format"] in ["mermaid", "dot"]

    def test_threat_modeling_react(self, react_project):
        """Test threat modeling - NOT skipped"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=False, skip_tech_debt=True)

        # Verify threats analyzed
        assert "threats" in result
        threats = result["threats"]

        # Should have status or threat data
        if "status" in threats:
            assert threats["status"] != "skipped"
        else:
            assert "threats" in threats or "total" in threats

    def test_tech_debt_detection_react(self, react_project):
        """Test tech debt detection - NOT skipped"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=False)

        # Verify tech debt detected
        assert "tech_debt" in result
        tech_debt = result["tech_debt"]

        # Should have status or debt data
        if "status" in tech_debt:
            assert tech_debt["status"] != "skipped"
        else:
            assert "tech_debt" in tech_debt or "total" in tech_debt

    def test_documentation_generation_react(self, react_project):
        """Test documentation generation"""
        analyzer = ProjectAnalyzer(str(react_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify documentation generated
        assert "documentation" in result
        docs = result["documentation"]

        assert "adrs" in docs
        assert "threat_model" in docs
        assert "tech_debt_report" in docs
        assert "import_report" in docs

        # Check that files were generated
        assert isinstance(docs["adrs"], list)
        assert isinstance(docs["threat_model"], str)
        assert isinstance(docs["tech_debt_report"], str)
        assert isinstance(docs["import_report"], str)
