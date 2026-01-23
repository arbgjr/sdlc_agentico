#!/usr/bin/env python3
"""
Integration tests for Go/Gin project analysis.

Tests the full sdlc-import workflow on a sample Go project.
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
def gin_project():
    """Create a minimal Go/Gin project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create go.mod
        create_file(
            project_path / "go.mod",
            """module github.com/example/myapi

go 1.21

require (
	github.com/gin-gonic/gin v1.9.1
	github.com/golang-jwt/jwt/v5 v5.0.0
	gorm.io/driver/postgres v1.5.4
	gorm.io/gorm v1.25.5
	github.com/joho/godotenv v1.5.1
)
"""
        )

        # Create main.go
        create_file(
            project_path / "main.go",
            """package main

import (
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

var db *gorm.DB

func main() {
	// Load .env file
	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	// Initialize database
	dsn := os.Getenv("DATABASE_URL")
	var err error
	db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// Auto-migrate models
	db.AutoMigrate(&User{}, &Product{})

	// Setup router
	router := gin.Default()

	// Public routes
	auth := router.Group("/api/auth")
	{
		auth.POST("/login", Login)
		auth.POST("/register", Register)
	}

	// Protected routes
	api := router.Group("/api")
	api.Use(AuthMiddleware())
	{
		api.GET("/users", GetUsers)
		api.GET("/users/:id", GetUser)
		api.POST("/users", CreateUser)
		api.PUT("/users/:id", UpdateUser)
		api.DELETE("/users/:id", DeleteUser)

		api.GET("/products", GetProducts)
		api.POST("/products", CreateProduct)
	}

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	router.Run(":" + port)
}
"""
        )

        # Create models.go
        create_file(
            project_path / "models.go",
            """package main

import (
	"time"

	"gorm.io/gorm"
)

type User struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
	Username  string         `gorm:"uniqueIndex;not null" json:"username"`
	Email     string         `gorm:"uniqueIndex;not null" json:"email"`
	Password  string         `gorm:"not null" json:"-"`
	Role      string         `gorm:"not null;default:'user'" json:"role"`
}

type Product struct {
	ID          uint           `gorm:"primarykey" json:"id"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"-"`
	Name        string         `gorm:"not null" json:"name"`
	Description string         `json:"description"`
	Price       float64        `gorm:"not null" json:"price"`
	Stock       int            `gorm:"not null;default:0" json:"stock"`
}
"""
        )

        # Create handlers.go
        create_file(
            project_path / "handlers.go",
            """package main

import (
	"net/http"
	"os"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type RegisterRequest struct {
	Username string `json:"username" binding:"required"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required,min=8"`
}

func Login(c *gin.Context) {
	var req LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	var user User
	if err := db.Where("username = ?", req.Username).First(&user).Error; err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	// Generate JWT token
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": user.ID,
		"role":    user.Role,
		"exp":     time.Now().Add(time.Hour * 24).Unix(),
	})

	tokenString, err := token.SignedString([]byte(os.Getenv("JWT_SECRET")))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"token": tokenString})
}

func Register(c *gin.Context) {
	var req RegisterRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	user := User{
		Username: req.Username,
		Email:    req.Email,
		Password: string(hashedPassword),
		Role:     "user",
	}

	if err := db.Create(&user).Error; err != nil {
		c.JSON(http.StatusConflict, gin.H{"error": "User already exists"})
		return
	}

	c.JSON(http.StatusCreated, user)
}

func GetUsers(c *gin.Context) {
	var users []User
	db.Find(&users)
	c.JSON(http.StatusOK, users)
}

func GetUser(c *gin.Context) {
	id := c.Param("id")
	var user User
	if err := db.First(&user, id).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	c.JSON(http.StatusOK, user)
}

func CreateUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := db.Create(&user).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, user)
}

func UpdateUser(c *gin.Context) {
	id := c.Param("id")
	var user User
	if err := db.First(&user, id).Error; err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	db.Save(&user)
	c.JSON(http.StatusOK, user)
}

func DeleteUser(c *gin.Context) {
	id := c.Param("id")
	if err := db.Delete(&User{}, id).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.Status(http.StatusNoContent)
}

func GetProducts(c *gin.Context) {
	var products []Product
	db.Find(&products)
	c.JSON(http.StatusOK, products)
}

func CreateProduct(c *gin.Context) {
	var product Product
	if err := c.ShouldBindJSON(&product); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := db.Create(&product).Error; err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, product)
}
"""
        )

        # Create middleware.go
        create_file(
            project_path / "middleware.go",
            """package main

import (
	"net/http"
	"os"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "No authorization header"})
			c.Abort()
			return
		}

		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid authorization header"})
			c.Abort()
			return
		}

		tokenString := parts[1]
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			return []byte(os.Getenv("JWT_SECRET")), nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		if claims, ok := token.Claims.(jwt.MapClaims); ok {
			c.Set("user_id", claims["user_id"])
			c.Set("role", claims["role"])
		}

		c.Next()
	}
}
"""
        )

        # Create .env.example
        create_file(
            project_path / ".env.example",
            """DATABASE_URL=postgresql://user:password@localhost:5432/mydb?sslmode=disable
JWT_SECRET=your-secret-key-here
PORT=8080
"""
        )

        # Create test file
        create_file(
            project_path / "handlers_test.go",
            """package main

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestGetUsers(t *testing.T) {
	gin.SetMode(gin.TestMode)

	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request, _ = http.NewRequest(http.MethodGet, "/api/users", nil)

	GetUsers(c)

	assert.Equal(t, http.StatusOK, w.Code)
}
"""
        )

        # Create README
        create_file(
            project_path / "README.md",
            """# Go Gin API

A sample REST API built with Go and Gin framework.
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


class TestGinIntegration:
    """Integration tests for Go/Gin project analysis"""

    def test_analyze_basic_structure(self, gin_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert result["project_path"] == str(gin_project)

    def test_branch_creation_gin(self, gin_project):
        """Test that feature branch is created"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        branch_name = result["branch"]["branch"]
        assert branch_name.startswith("feature/import-")
        assert result["branch"]["created"] is True

    def test_directory_scan_gin(self, gin_project):
        """Test directory scanning"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        scan = result["scan"]
        assert scan["total_files"] >= 4
        assert ".go" in scan["files_by_extension"]

        go_info = scan["files_by_extension"][".go"]
        assert go_info["count"] >= 4
        assert go_info["loc"] > 0

    def test_project_validation_gin(self, gin_project):
        """Test project validation"""
        analyzer = ProjectAnalyzer(str(gin_project))
        assert analyzer.validate_project() is True

    def test_language_detection_gin(self, gin_project):
        """Test language detection"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        lang_analysis = result["language_analysis"]
        assert lang_analysis["primary_language"] == "go"
        assert "go" in lang_analysis["languages"]
        assert lang_analysis["languages"]["go"]["percentage"] > 50

    def test_decision_extraction_gin(self, gin_project):
        """Test decision extraction"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        decisions = result["decisions"]
        assert "count" in decisions
        assert decisions["count"] >= 0

    def test_diagram_generation_gin(self, gin_project):
        """Test diagram generation"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        diagrams = result["diagrams"]
        assert isinstance(diagrams["diagrams"], list)

    def test_threat_modeling_gin(self, gin_project):
        """Test threat modeling"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=False, skip_tech_debt=True)

        threats = result["threats"]
        if "status" in threats:
            assert threats["status"] != "skipped"

    def test_tech_debt_detection_gin(self, gin_project):
        """Test tech debt detection"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=False)

        tech_debt = result["tech_debt"]
        if "status" in tech_debt:
            assert tech_debt["status"] != "skipped"

    def test_documentation_generation_gin(self, gin_project):
        """Test documentation generation"""
        analyzer = ProjectAnalyzer(str(gin_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        docs = result["documentation"]
        assert isinstance(docs["adrs"], list)
        assert isinstance(docs["threat_model"], str)
        assert isinstance(docs["tech_debt_report"], str)
        assert isinstance(docs["import_report"], str)
