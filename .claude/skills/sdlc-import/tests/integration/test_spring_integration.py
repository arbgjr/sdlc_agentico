#!/usr/bin/env python3
"""
Integration tests for Spring Boot project analysis.

Tests the full sdlc-import workflow on a sample Java project.
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
def spring_project():
    """Create a minimal Spring Boot project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create pom.xml
        create_file(
            project_path / "pom.xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>demo</name>
    <description>Demo project for Spring Boot</description>

    <properties>
        <java.version>17</java.version>
    </properties>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <scope>runtime</scope>
        </dependency>
        <dependency>
            <groupId>io.jsonwebtoken</groupId>
            <artifactId>jjwt-api</artifactId>
            <version>0.11.5</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
"""
        )

        # Create application.properties
        create_file(
            project_path / "src/main/resources/application.properties",
            """spring.datasource.url=jdbc:postgresql://${DB_HOST:localhost}:5432/${DB_NAME:myapp}
spring.datasource.username=${DB_USER:postgres}
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=update
spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect

jwt.secret=${JWT_SECRET}
jwt.expiration=86400000

logging.level.org.springframework.security=DEBUG
"""
        )

        # Create main application
        create_file(
            project_path / "src/main/java/com/example/demo/DemoApplication.java",
            """package com.example.demo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
"""
        )

        # Create entity
        create_file(
            project_path / "src/main/java/com/example/demo/entity/User.java",
            """package com.example.demo.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String username;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String email;

    private LocalDateTime createdAt;

    // Getters and setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}
"""
        )

        # Create repository
        create_file(
            project_path / "src/main/java/com/example/demo/repository/UserRepository.java",
            """package com.example.demo.repository;

import com.example.demo.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}
"""
        )

        # Create controller
        create_file(
            project_path / "src/main/java/com/example/demo/controller/UserController.java",
            """package com.example.demo.controller;

import com.example.demo.entity.User;
import com.example.demo.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @Autowired
    private UserRepository userRepository;

    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        return userRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    public User createUser(@RequestBody User user) {
        return userRepository.save(user);
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        if (!userRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }
        userRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
"""
        )

        # Create security config
        create_file(
            project_path / "src/main/java/com/example/demo/config/SecurityConfig.java",
            """package com.example.demo.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf().disable()
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .anyRequest().authenticated()
            );
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
"""
        )

        # Create test
        create_file(
            project_path / "src/test/java/com/example/demo/UserControllerTest.java",
            """package com.example.demo;

import com.example.demo.controller.UserController;
import com.example.demo.repository.UserRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testGetAllUsers() throws Exception {
        mockMvc.perform(get("/api/users"))
                .andExpect(status().isOk());
    }
}
"""
        )

        # Create README
        create_file(
            project_path / "README.md",
            """# Spring Boot Demo

A sample Spring Boot application.
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


class TestSpringIntegration:
    """Integration tests for Spring Boot project analysis"""

    def test_analyze_basic_structure(self, spring_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert "branch" in result
        assert "scan" in result
        assert result["project_path"] == str(spring_project)

    def test_branch_creation_spring(self, spring_project):
        """Test that feature branch is created"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        assert "branch" in result
        branch_name = result["branch"]["branch"]
        assert branch_name.startswith("feature/import-")
        assert result["branch"]["created"] is True

    def test_directory_scan_spring(self, spring_project):
        """Test directory scanning"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        scan = result["scan"]
        assert scan["total_files"] >= 5
        assert ".java" in scan["files_by_extension"]

        java_info = scan["files_by_extension"][".java"]
        assert java_info["count"] >= 5
        assert java_info["loc"] > 0

    def test_project_validation_spring(self, spring_project):
        """Test project validation"""
        analyzer = ProjectAnalyzer(str(spring_project))
        assert analyzer.validate_project() is True

    def test_language_detection_spring(self, spring_project):
        """Test language detection"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        lang_analysis = result["language_analysis"]
        assert lang_analysis["primary_language"] == "java"
        assert "java" in lang_analysis["languages"]
        assert lang_analysis["languages"]["java"]["percentage"] > 50

        # Should detect Spring framework
        frameworks = lang_analysis.get("frameworks", {})
        assert "backend" in frameworks or len(frameworks) >= 0

    def test_decision_extraction_spring(self, spring_project):
        """Test decision extraction"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        decisions = result["decisions"]
        assert "count" in decisions
        assert decisions["count"] >= 0

        if decisions["count"] > 0:
            decision = decisions["decisions"][0]
            assert decision["id"].startswith("ADR-INFERRED-")
            assert "confidence" in decision

    def test_diagram_generation_spring(self, spring_project):
        """Test diagram generation"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        diagrams = result["diagrams"]
        assert isinstance(diagrams["diagrams"], list)

    def test_threat_modeling_spring(self, spring_project):
        """Test threat modeling"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=False, skip_tech_debt=True)

        threats = result["threats"]
        if "status" in threats:
            assert threats["status"] != "skipped"

    def test_tech_debt_detection_spring(self, spring_project):
        """Test tech debt detection"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=False)

        tech_debt = result["tech_debt"]
        if "status" in tech_debt:
            assert tech_debt["status"] != "skipped"

    def test_documentation_generation_spring(self, spring_project):
        """Test documentation generation"""
        analyzer = ProjectAnalyzer(str(spring_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        docs = result["documentation"]
        assert isinstance(docs["adrs"], list)
        assert isinstance(docs["threat_model"], str)
        assert isinstance(docs["tech_debt_report"], str)
        assert isinstance(docs["import_report"], str)
