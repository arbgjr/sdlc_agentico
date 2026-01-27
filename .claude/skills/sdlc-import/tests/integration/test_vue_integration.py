#!/usr/bin/env python3
"""
Integration tests for Vue.js project analysis.

Tests the full sdlc-import workflow on a sample Vue.js project.
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
def vue_project():
    """Create a minimal Vue.js project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create package.json
        create_file(
            project_path / "package.json",
            """{
  "name": "my-vue-app",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "pinia": "^2.1.6"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.3.4",
    "vite": "^4.4.9"
  }
}
"""
        )

        # Create vite.config.js
        create_file(
            project_path / "vite.config.js",
            """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})
"""
        )

        # Create main.js
        create_file(
            project_path / "src/main.js",
            """import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
"""
        )

        # Create App.vue
        create_file(
            project_path / "src/App.vue",
            """<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/about">About</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  console.log('App mounted')
})
</script>

<style scoped>
nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}
</style>
"""
        )

        # Create Home view
        create_file(
            project_path / "src/views/HomeView.vue",
            """<template>
  <div class="home">
    <h1>{{ title }}</h1>
    <p>{{ message }}</p>
    <button @click="increment">Count: {{ count }}</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('Welcome to Vue 3')
const message = ref('This is the home page')
const count = ref(0)

const increment = () => {
  count.value++
}
</script>

<style scoped>
.home {
  text-align: center;
  margin-top: 50px;
}
</style>
"""
        )

        # Create router
        create_file(
            project_path / "src/router/index.js",
            """import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router
"""
        )

        # Create Pinia store
        create_file(
            project_path / "src/stores/counter.js",
            """import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)

  function increment() {
    count.value++
  }

  return { count, doubleCount, increment }
})
"""
        )

        create_file(
            project_path / "README.md",
            """# My Vue App

A Vue.js 3 application using Composition API.
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


class TestVueIntegration:
    """Integration tests for Vue.js project analysis"""

    def test_analyze_basic_structure(self, vue_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(vue_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify basic structure
        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result

    def test_language_detection_javascript(self, vue_project):
        """Test JavaScript language detection"""
        analyzer = ProjectAnalyzer(str(vue_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify language detection
        assert "language_analysis" in result
        lang_analysis = result["language_analysis"]

        assert "primary_language" in lang_analysis
        # Primary language should be JavaScript
        assert lang_analysis["primary_language"] in ["javascript", "vue"]

    def test_vue_framework_detection(self, vue_project):
        """Test Vue.js framework detection"""
        analyzer = ProjectAnalyzer(str(vue_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify framework detection
        assert "language_analysis" in result
        frameworks = result["language_analysis"]["frameworks"]

        # Vue should be detected as frontend framework
        assert "frontend" in frameworks
        frontend_frameworks = [f.lower() for f in frameworks["frontend"]]
        assert "vue" in frontend_frameworks

    def test_vite_build_tool_detection(self, vue_project):
        """Test Vite build tool detection"""
        analyzer = ProjectAnalyzer(str(vue_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify build tool detection
        frameworks = result["language_analysis"]["frameworks"]

        # Vite should be detected as build tool
        assert "build_tools" in frameworks
        build_tools = [f.lower() for f in frameworks["build_tools"]]
        assert "vite" in build_tools

    def test_file_count_vue(self, vue_project):
        """Test that Vue files are counted correctly"""
        analyzer = ProjectAnalyzer(str(vue_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        # Verify scan results
        scan = result["scan"]
        files_by_ext = scan["files_by_extension"]

        # Should detect .vue files
        assert ".vue" in files_by_ext
        assert files_by_ext[".vue"]["count"] >= 2

        # Should detect .js files
        assert ".js" in files_by_ext
        assert files_by_ext[".js"]["count"] >= 3
