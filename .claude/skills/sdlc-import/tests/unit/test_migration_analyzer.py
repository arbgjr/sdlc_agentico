import pytest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from migration_analyzer import MigrationAnalyzer


class TestMigrationAnalyzer:
    @pytest.fixture
    def analyzer(self):
        config = {
            "migration_analysis": {"enabled": True}
        }
        return MigrationAnalyzer(config)

    def test_ef_core_table_detection(self, analyzer, tmp_path):
        """Test EF Core table creation detection"""
        # Create test migration file
        migration_file = tmp_path / "Migrations" / "20260123_CreateUsers.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            public partial class CreateUsers : Migration
            {
                protected override void Up(MigrationBuilder migrationBuilder)
                {
                    migrationBuilder.CreateTable(
                        name: "Users",
                        columns: table => new
                        {
                            Id = table.Column<Guid>(nullable: false),
                            Name = table.Column<string>(maxLength: 100, nullable: false)
                        },
                        constraints: table =>
                        {
                            table.PrimaryKey("PK_Users", x => x.Id);
                        });
                }
            }
        """)

        result = analyzer.analyze(tmp_path)
        assert result['count'] > 0
        assert result['by_framework']['ef_core'] == 1

        # Check decision details
        decision = result['decisions'][0]
        assert decision['category'] == 'data_model'
        assert 'Users' in decision['title']
        assert decision['confidence'] == 0.95

    def test_ef_core_index_detection(self, analyzer, tmp_path):
        """Test EF Core index creation detection"""
        migration_file = tmp_path / "Migrations" / "20260123_AddIndexes.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            public partial class AddIndexes : Migration
            {
                protected override void Up(MigrationBuilder migrationBuilder)
                {
                    migrationBuilder.CreateIndex(
                        name: "IX_Users_Email",
                        table: "Users",
                        column: "Email",
                        unique: true);
                }
            }
        """)

        result = analyzer.analyze(tmp_path)
        assert result['count'] > 0
        assert result['by_framework']['ef_core'] == 1

        decision = result['decisions'][0]
        assert decision['category'] == 'performance'
        assert 'IX_Users_Email' in decision['title']

    def test_ef_core_rls_detection(self, analyzer, tmp_path):
        """Test EF Core RLS policy detection"""
        migration_file = tmp_path / "Migrations" / "20260123_AddRLS.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            public partial class AddRLS : Migration
            {
                protected override void Up(MigrationBuilder migrationBuilder)
                {
                    migrationBuilder.Sql(@"
                        ALTER TABLE Users ENABLE ROW LEVEL SECURITY;
                        CREATE POLICY tenant_isolation ON Users
                        FOR ALL TO PUBLIC
                        USING (tenant_id = current_setting('app.tenant_id')::uuid);
                    ");
                }
            }
        """)

        result = analyzer.analyze(tmp_path)
        assert result['count'] > 0
        assert result['by_framework']['ef_core'] == 1

        decision = result['decisions'][0]
        assert decision['category'] == 'security'
        assert decision['confidence'] == 1.0
        assert 'Row-Level Security' in decision['title']

    def test_alembic_table_detection(self, analyzer, tmp_path):
        """Test Alembic table creation detection"""
        migration_file = tmp_path / "alembic" / "versions" / "abc123_create_users.py"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            def upgrade():
                op.create_table('users',
                    sa.Column('id', sa.UUID(), nullable=False),
                    sa.Column('name', sa.String(length=100), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                )
        """)

        result = analyzer.analyze(tmp_path)
        assert result['by_framework']['alembic'] == 1

        decision = result['decisions'][0]
        assert decision['framework'] == 'Alembic'
        assert 'users' in decision['title']

    def test_alembic_index_detection(self, analyzer, tmp_path):
        """Test Alembic index creation detection"""
        migration_file = tmp_path / "alembic" / "versions" / "def456_add_indexes.py"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            def upgrade():
                op.create_index('ix_users_email', 'users', ['email'], unique=True)
        """)

        result = analyzer.analyze(tmp_path)
        assert result['by_framework']['alembic'] == 1

        decision = result['decisions'][0]
        assert decision['category'] == 'performance'

    def test_flyway_table_detection(self, analyzer, tmp_path):
        """Test Flyway table creation detection"""
        migration_file = tmp_path / "db" / "migration" / "V1__create_users.sql"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """)

        result = analyzer.analyze(tmp_path)
        assert result['by_framework']['flyway'] == 1

        decision = result['decisions'][0]
        assert decision['framework'] == 'Flyway'
        assert 'users' in decision['title']

    def test_flyway_index_detection(self, analyzer, tmp_path):
        """Test Flyway index creation detection"""
        migration_file = tmp_path / "db" / "migration" / "V2__add_indexes.sql"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            CREATE UNIQUE INDEX ix_users_email ON users(email);
        """)

        result = analyzer.analyze(tmp_path)
        assert result['by_framework']['flyway'] == 1

        decision = result['decisions'][0]
        assert decision['category'] == 'performance'

    def test_flyway_rls_detection(self, analyzer, tmp_path):
        """Test Flyway RLS policy detection"""
        migration_file = tmp_path / "db" / "migration" / "V3__add_rls.sql"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            ALTER TABLE users ENABLE ROW LEVEL SECURITY;

            CREATE POLICY tenant_isolation ON users
            FOR ALL TO PUBLIC
            USING (tenant_id = current_setting('app.tenant_id')::uuid);
        """)

        result = analyzer.analyze(tmp_path)
        assert result['by_framework']['flyway'] == 1

        decision = result['decisions'][0]
        assert decision['category'] == 'security'
        assert decision['confidence'] == 1.0

    def test_multiple_frameworks(self, analyzer, tmp_path):
        """Test analysis with multiple frameworks present"""
        # Create EF Core migration
        ef_file = tmp_path / "Migrations" / "20260123_CreateUsers.cs"
        ef_file.parent.mkdir(parents=True)
        ef_file.write_text("""
            migrationBuilder.CreateTable(
                name: "Users",
                columns: table => new { Id = table.Column<Guid>() });
        """)

        # Create Alembic migration
        alembic_file = tmp_path / "alembic" / "versions" / "abc_create_posts.py"
        alembic_file.parent.mkdir(parents=True)
        alembic_file.write_text("""
            op.create_table('posts', sa.Column('id', sa.UUID()))
        """)

        result = analyzer.analyze(tmp_path)
        assert result['count'] == 2
        assert result['by_framework']['ef_core'] == 1
        assert result['by_framework']['alembic'] == 1

    def test_empty_project(self, analyzer, tmp_path):
        """Test analysis with no migrations"""
        result = analyzer.analyze(tmp_path)
        assert result['count'] == 0
        assert result['by_framework']['ef_core'] == 0
        assert result['by_framework']['alembic'] == 0
        assert result['by_framework']['flyway'] == 0

    def test_disabled_analysis(self, tmp_path):
        """Test that disabled analysis doesn't process files"""
        config = {"migration_analysis": {"enabled": False}}
        analyzer = MigrationAnalyzer(config)
        assert analyzer.enabled is False

    def test_invalid_migration_file(self, analyzer, tmp_path):
        """Test handling of invalid migration files"""
        # Create malformed migration
        migration_file = tmp_path / "Migrations" / "20260123_Invalid.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("This is not valid C# code!!!!")

        # Should not crash, just log warning
        result = analyzer.analyze(tmp_path)
        assert result['count'] == 0

    def test_decision_id_generation(self, analyzer, tmp_path):
        """Test that decision IDs are properly generated"""
        migration_file = tmp_path / "Migrations" / "20260123_CreateUsers.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            migrationBuilder.CreateTable(
                name: "Users",
                columns: table => new { Id = table.Column<Guid>() });
        """)

        result = analyzer.analyze(tmp_path)
        decision = result['decisions'][0]

        assert 'id' in decision
        assert decision['id'].startswith('ADR-INFERRED-MIGRATION')
        assert 'Users' in decision['id']

    def test_evidence_tracking(self, analyzer, tmp_path):
        """Test that evidence is properly tracked"""
        migration_file = tmp_path / "Migrations" / "20260123_CreateUsers.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            migrationBuilder.CreateTable(
                name: "Users",
                columns: table => new { Id = table.Column<Guid>() });
        """)

        result = analyzer.analyze(tmp_path)
        decision = result['decisions'][0]

        assert 'evidence' in decision
        assert len(decision['evidence']) > 0
        assert decision['evidence'][0]['source'] == 'migration'
        assert decision['evidence'][0]['quality'] == 1.0
