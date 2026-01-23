#!/usr/bin/env python3
"""
Integration tests for Playwright project analysis.

Tests the full sdlc-import workflow on a sample Playwright E2E testing project.
Tests multi-language testing framework detection (TypeScript Playwright).
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
def playwright_project():
    """Create a minimal Playwright E2E testing project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create package.json
        create_file(
            project_path / "package.json",
            """{
  "name": "e2e-tests",
  "version": "1.0.0",
  "description": "E2E tests using Playwright",
  "scripts": {
    "test": "playwright test",
    "test:headed": "playwright test --headed",
    "test:debug": "playwright test --debug"
  },
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "@types/node": "^20.10.0",
    "typescript": "^5.3.2"
  }
}
"""
        )

        # Create playwright.config.ts
        create_file(
            project_path / "playwright.config.ts",
            """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
});
"""
        )

        # Create test files
        create_file(
            project_path / "tests/home.spec.ts",
            """import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should display welcome message', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('h1')).toContainText('Welcome');
  });

  test('should navigate to about page', async ({ page }) => {
    await page.goto('/');

    await page.click('a[href="/about"]');

    await expect(page).toHaveURL('/about');
    await expect(page.locator('h1')).toContainText('About');
  });
});
"""
        )

        create_file(
            project_path / "tests/login.spec.ts",
            """import { test, expect } from '@playwright/test';

test.describe('Login Flow', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'user@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.user-name')).toContainText('User');
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await page.fill('input[name="email"]', 'invalid@example.com');
    await page.fill('input[name="password"]', 'wrong');
    await page.click('button[type="submit"]');

    await expect(page.locator('.error-message')).toBeVisible();
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');
  });
});
"""
        )

        create_file(
            project_path / "tests/api.spec.ts",
            """import { test, expect } from '@playwright/test';

test.describe('API Tests', () => {
  test('should fetch user data', async ({ request }) => {
    const response = await request.get('/api/users/1');

    expect(response.status()).toBe(200);

    const data = await response.json();
    expect(data).toHaveProperty('id', 1);
    expect(data).toHaveProperty('name');
    expect(data).toHaveProperty('email');
  });
});
"""
        )

        # Create helper/fixture file
        create_file(
            project_path / "tests/fixtures.ts",
            """import { test as base } from '@playwright/test';

export type TestFixtures = {
  authenticatedPage: any;
};

export const test = base.extend<TestFixtures>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'user@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    await use(page);
  },
});

export { expect } from '@playwright/test';
"""
        )

        # Create tsconfig.json
        create_file(
            project_path / "tsconfig.json",
            """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["tests/**/*.ts"]
}
"""
        )

        create_file(
            project_path / "README.md",
            """# E2E Tests

Playwright E2E tests for web application.
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


class TestPlaywrightIntegration:
    """Integration tests for Playwright project analysis"""

    def test_analyze_basic_structure(self, playwright_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(playwright_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify basic structure
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result

    def test_language_detection_typescript(self, playwright_project):
        """Test TypeScript language detection"""
        analyzer = ProjectAnalyzer(str(playwright_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify language detection
        assert "language_analysis" in result
        lang_analysis = result["language_analysis"]

        assert "primary_language" in lang_analysis
        assert lang_analysis["primary_language"] == "typescript"

        assert "languages" in lang_analysis
        assert "typescript" in lang_analysis["languages"]

    def test_playwright_testing_framework_detection(self, playwright_project):
        """Test Playwright testing framework detection"""
        analyzer = ProjectAnalyzer(str(playwright_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify framework detection
        assert "language_analysis" in result
        frameworks = result["language_analysis"]["frameworks"]

        # Playwright should be detected as testing framework
        assert "testing" in frameworks
        testing_frameworks = [f.lower() for f in frameworks["testing"]]
        assert "playwright" in testing_frameworks

    def test_file_count_typescript(self, playwright_project):
        """Test that TypeScript files are counted correctly"""
        analyzer = ProjectAnalyzer(str(playwright_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify scan results
        scan = result["scan"]
        files_by_ext = scan["files_by_extension"]

        # Should detect .ts files
        assert ".ts" in files_by_ext
        assert files_by_ext[".ts"]["count"] >= 5
