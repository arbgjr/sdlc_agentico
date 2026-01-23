#!/usr/bin/env python3
"""
Integration tests for ASP.NET Core project analysis.

Tests the full sdlc-import workflow on a sample C# project.
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
def aspnet_project():
    """Create a minimal ASP.NET Core project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create .csproj
        create_file(
            project_path / "MyWebApi.csproj",
            """<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Design" Version="8.0.0">
      <PrivateAssets>all</PrivateAssets>
    </PackageReference>
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.5.0" />
    <PackageReference Include="Serilog.AspNetCore" Version="8.0.0" />
  </ItemGroup>

</Project>
"""
        )

        # Create appsettings.json
        create_file(
            project_path / "appsettings.json",
            """{
  "ConnectionStrings": {
    "DefaultConnection": "Server=${SQL_SERVER:localhost};Database=${SQL_DATABASE:MyDb};User Id=${SQL_USER:sa};Password=${SQL_PASSWORD};TrustServerCertificate=true"
  },
  "Jwt": {
    "Secret": "${JWT_SECRET}",
    "Issuer": "MyWebApi",
    "Audience": "MyWebApi",
    "ExpirationMinutes": 60
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
"""
        )

        # Create Program.cs
        create_file(
            project_path / "Program.cs",
            """using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Serilog;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

// Configure Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .CreateLogger();

builder.Host.UseSerilog();

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure Database
builder.Services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// Configure JWT Authentication
var jwtSecret = builder.Configuration["Jwt:Secret"];
var key = Encoding.ASCII.GetBytes(jwtSecret!);

builder.Services.AddAuthentication(x =>
{
    x.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    x.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(x =>
{
    x.RequireHttpsMetadata = false;
    x.SaveToken = true;
    x.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(key),
        ValidateIssuer = true,
        ValidateAudience = true,
        ValidIssuer = builder.Configuration["Jwt:Issuer"],
        ValidAudience = builder.Configuration["Jwt:Audience"],
        ClockSkew = TimeSpan.Zero
    };
});

builder.Services.AddAuthorization();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
"""
        )

        # Create DbContext
        create_file(
            project_path / "Data/ApplicationDbContext.cs",
            """using Microsoft.EntityFrameworkCore;

public class ApplicationDbContext : DbContext
{
    public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
        : base(options)
    {
    }

    public DbSet<User> Users { get; set; } = null!;
    public DbSet<Product> Products { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Email).IsUnique();
            entity.Property(e => e.Username).IsRequired().HasMaxLength(100);
            entity.Property(e => e.Email).IsRequired().HasMaxLength(255);
            entity.Property(e => e.PasswordHash).IsRequired();
        });

        modelBuilder.Entity<Product>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Price).HasPrecision(18, 2);
        });
    }
}
"""
        )

        # Create Models
        create_file(
            project_path / "Models/User.cs",
            """using System.ComponentModel.DataAnnotations;

public class User
{
    public int Id { get; set; }

    [Required]
    [MaxLength(100)]
    public string Username { get; set; } = string.Empty;

    [Required]
    [EmailAddress]
    [MaxLength(255)]
    public string Email { get; set; } = string.Empty;

    [Required]
    public string PasswordHash { get; set; } = string.Empty;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public bool IsActive { get; set; } = true;
}
"""
        )

        create_file(
            project_path / "Models/Product.cs",
            """using System.ComponentModel.DataAnnotations;

public class Product
{
    public int Id { get; set; }

    [Required]
    [MaxLength(200)]
    public string Name { get; set; } = string.Empty;

    public string? Description { get; set; }

    [Range(0.01, double.MaxValue)]
    public decimal Price { get; set; }

    public int Stock { get; set; }

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
"""
        )

        # Create Controller
        create_file(
            project_path / "Controllers/UsersController.cs",
            """using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace MyWebApi.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UsersController : ControllerBase
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<UsersController> _logger;

    public UsersController(ApplicationDbContext context, ILogger<UsersController> logger)
    {
        _context = context;
        _logger = logger;
    }

    [HttpGet]
    [Authorize(Roles = "Admin")]
    public async Task<ActionResult<IEnumerable<User>>> GetUsers()
    {
        _logger.LogInformation("Fetching all users");
        return await _context.Users.ToListAsync();
    }

    [HttpGet("{id}")]
    public async Task<ActionResult<User>> GetUser(int id)
    {
        var user = await _context.Users.FindAsync(id);

        if (user == null)
        {
            _logger.LogWarning("User {UserId} not found", id);
            return NotFound();
        }

        return user;
    }

    [HttpPost]
    [Authorize(Roles = "Admin")]
    public async Task<ActionResult<User>> CreateUser(User user)
    {
        _context.Users.Add(user);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Created user {UserId}", user.Id);
        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }

    [HttpDelete("{id}")]
    [Authorize(Roles = "Admin")]
    public async Task<IActionResult> DeleteUser(int id)
    {
        var user = await _context.Users.FindAsync(id);
        if (user == null)
        {
            return NotFound();
        }

        _context.Users.Remove(user);
        await _context.SaveChangesAsync();

        _logger.LogInformation("Deleted user {UserId}", id);
        return NoContent();
    }
}
"""
        )

        # Create test
        create_file(
            project_path / "Tests/UsersControllerTests.cs",
            """using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace MyWebApi.Tests;

public class UsersControllerTests
{
    [Fact]
    public async Task GetUsers_ReturnsAllUsers()
    {
        // Arrange
        var options = new DbContextOptionsBuilder<ApplicationDbContext>()
            .UseInMemoryDatabase(databaseName: "TestDb")
            .Options;

        using var context = new ApplicationDbContext(options);
        var logger = new Mock<ILogger<UsersController>>();
        var controller = new UsersController(context, logger.Object);

        // Act
        var result = await controller.GetUsers();

        // Assert
        Assert.NotNull(result);
    }
}
"""
        )

        # Create README
        create_file(
            project_path / "README.md",
            """# ASP.NET Core Web API

A sample ASP.NET Core Web API project.
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


class TestAspNetIntegration:
    """Integration tests for ASP.NET Core project analysis"""

    def test_analyze_basic_structure(self, aspnet_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert result["project_path"] == str(aspnet_project)

    def test_branch_creation_aspnet(self, aspnet_project):
        """Test that feature branch is created"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        branch_name = result["branch"]["branch"]
        assert branch_name.startswith("feature/import-")
        assert result["branch"]["created"] is True

    def test_directory_scan_aspnet(self, aspnet_project):
        """Test directory scanning"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        scan = result["scan"]
        assert scan["total_files"] >= 5
        assert ".cs" in scan["files_by_extension"]

        cs_info = scan["files_by_extension"][".cs"]
        assert cs_info["count"] >= 4
        assert cs_info["loc"] > 0

    def test_project_validation_aspnet(self, aspnet_project):
        """Test project validation"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        assert analyzer.validate_project() is True

    def test_language_detection_aspnet(self, aspnet_project):
        """Test language detection"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        lang_analysis = result["language_analysis"]
        assert lang_analysis["primary_language"] == "csharp"
        assert "csharp" in lang_analysis["languages"]
        assert lang_analysis["languages"]["csharp"]["percentage"] > 50

    def test_decision_extraction_aspnet(self, aspnet_project):
        """Test decision extraction"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        decisions = result["decisions"]
        assert "count" in decisions
        assert decisions["count"] >= 0

    def test_diagram_generation_aspnet(self, aspnet_project):
        """Test diagram generation"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        diagrams = result["diagrams"]
        assert isinstance(diagrams["diagrams"], list)

    def test_threat_modeling_aspnet(self, aspnet_project):
        """Test threat modeling"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=False, skip_tech_debt=True)

        threats = result["threats"]
        if "status" in threats:
            assert threats["status"] != "skipped"

    def test_tech_debt_detection_aspnet(self, aspnet_project):
        """Test tech debt detection"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=False)

        tech_debt = result["tech_debt"]
        if "status" in tech_debt:
            assert tech_debt["status"] != "skipped"

    def test_documentation_generation_aspnet(self, aspnet_project):
        """Test documentation generation"""
        analyzer = ProjectAnalyzer(str(aspnet_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        docs = result["documentation"]
        assert isinstance(docs["adrs"], list)
        assert isinstance(docs["threat_model"], str)
        assert isinstance(docs["tech_debt_report"], str)
        assert isinstance(docs["import_report"], str)
