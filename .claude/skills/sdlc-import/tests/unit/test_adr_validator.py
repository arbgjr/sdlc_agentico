import pytest
from pathlib import Path
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from adr_validator import ADRValidator


class TestADRValidator:
    @pytest.fixture
    def validator(self):
        config = {"adr_validation": {"enabled": True}}
        return ADRValidator(config)

    def test_lgpd_coverage_validation_success(self, validator, tmp_path):
        """Test successful LGPD coverage validation"""
        # Create test file with LGPD implementation
        lgpd_file = tmp_path / "Services" / "DataSubjectRightService.cs"
        lgpd_file.parent.mkdir(parents=True)
        lgpd_file.write_text("""
            public class DataSubjectRightService {
                public void RequestDataDeletion() {}
                public void RequestDataPortability() {}
                public void RevokeConsent() {}
            }
        """)

        # Create ADR with LGPD claim (3/8 methods = 37.5%)
        adr = {
            "id": "ADR-TEST-001",
            "title": "LGPD Compliance",
            "decision": "Implement LGPD coverage 37%"
        }

        result = validator.validate(tmp_path, [adr])

        assert result['summary']['total_claims'] > 0
        assert result['summary']['validation_rate'] > 0  # Should validate successfully

    def test_lgpd_coverage_validation_failure(self, validator, tmp_path):
        """Test failed LGPD coverage validation (claim vs reality mismatch)"""
        # Create minimal LGPD implementation (1 method)
        lgpd_file = tmp_path / "Services" / "DataSubjectRightService.cs"
        lgpd_file.parent.mkdir(parents=True)
        lgpd_file.write_text("""
            public class DataSubjectRightService {
                public void RequestDataDeletion() {}
            }
        """)

        # Claim 95% coverage but only have 12.5% (1/8)
        adr = {
            "id": "ADR-TEST-001",
            "title": "LGPD Compliance",
            "decision": "Implement LGPD coverage 95%"
        }

        result = validator.validate(tmp_path, [adr])
        claim_result = result['results'][0]['claims'][0]

        assert claim_result['is_valid'] is False
        assert claim_result['actual_coverage'] < claim_result['claimed_coverage']
        assert claim_result['confidence'] < 0.5

    def test_rls_technology_validation_success(self, validator, tmp_path):
        """Test successful RLS technology validation"""
        # Create migration with RLS
        migration_file = tmp_path / "Migrations" / "AddRLS.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("""
            migrationBuilder.Sql(@"
                ALTER TABLE users ENABLE ROW LEVEL SECURITY;
                CREATE POLICY tenant_isolation ON users FOR ALL TO PUBLIC
                USING (tenant_id = current_setting('app.tenant_id')::uuid);
            ");
        """)

        # ADR claiming RLS usage
        adr = {
            "id": "ADR-TEST-002",
            "title": "Multi-Tenancy",
            "decision": "Uses PostgreSQL Row-Level Security for tenant isolation"
        }

        result = validator.validate(tmp_path, [adr])
        claim_result = result['results'][0]['claims'][0]

        assert claim_result['is_valid'] is True
        assert claim_result['confidence'] >= 0.9
        assert len(claim_result['evidence_files']) > 0

    def test_rls_technology_validation_failure(self, validator, tmp_path):
        """Test failed RLS technology validation (no RLS implementation)"""
        adr = {
            "id": "ADR-TEST-003",
            "title": "Multi-Tenancy",
            "decision": "Uses Row-Level Security"
        }

        result = validator.validate(tmp_path, [adr])
        claim_result = result['results'][0]['claims'][0]

        assert claim_result['is_valid'] is False
        assert claim_result['confidence'] < 0.5

    def test_jwt_technology_validation(self, validator, tmp_path):
        """Test JWT technology validation"""
        auth_file = tmp_path / "Services" / "AuthService.cs"
        auth_file.parent.mkdir(parents=True)
        auth_file.write_text("""
            using Microsoft.IdentityModel.Tokens;

            public class AuthService {
                private JwtSecurityTokenHandler tokenHandler = new JwtSecurityTokenHandler();
            }
        """)

        adr = {
            "id": "ADR-TEST-004",
            "title": "Authentication",
            "decision": "Uses JWT for authentication"
        }

        result = validator.validate(tmp_path, [adr])
        claim_result = result['results'][0]['claims'][0]

        assert claim_result['is_valid'] is True
        assert claim_result['confidence'] >= 0.8

    def test_multi_tenancy_validation(self, validator, tmp_path):
        """Test multi-tenancy pattern validation"""
        # Create files with tenant_id patterns
        model_file = tmp_path / "Models" / "User.cs"
        model_file.parent.mkdir(parents=True)
        model_file.write_text("""
            public class User {
                public Guid TenantId { get; set; }
                public string Name { get; set; }
            }
        """)

        service_file = tmp_path / "Services" / "UserService.cs"
        service_file.parent.mkdir(parents=True)
        service_file.write_text("""
            public class UserService {
                public async Task<User> GetUser(Guid userId, Guid tenantId) {
                    return await _db.Users.Where(u => u.TenantId == tenantId).FirstOrDefaultAsync();
                }
            }
        """)

        adr = {
            "id": "ADR-TEST-005",
            "title": "Multi-Tenancy",
            "decision": "Implements multi-tenancy with tenant isolation"
        }

        result = validator.validate(tmp_path, [adr])
        claim_result = result['results'][0]['claims'][0]

        assert claim_result['is_valid'] is True
        assert claim_result['occurrences'] >= 3

    def test_claim_extraction_coverage(self, validator):
        """Test extraction of coverage claims from ADR"""
        adr = {
            "id": "ADR-001",
            "decision": "We achieved LGPD coverage 95% with data subject rights implementation"
        }

        claims = validator._extract_claims(adr)

        assert len(claims) > 0
        assert claims[0]['type'] == 'coverage'
        assert claims[0]['framework'] == 'LGPD'
        assert claims[0]['claimed_percentage'] == 95

    def test_claim_extraction_technology(self, validator):
        """Test extraction of technology claims from ADR"""
        adr = {
            "id": "ADR-002",
            "decision": "System uses Row-Level Security for data isolation"
        }

        claims = validator._extract_claims(adr)

        assert len(claims) > 0
        assert claims[0]['type'] == 'technology'
        assert claims[0]['technology'] == 'Row-Level Security'

    def test_multiple_claims_in_single_adr(self, validator):
        """Test ADR with multiple claims"""
        adr = {
            "id": "ADR-003",
            "decision": "Achieved LGPD coverage 80% and uses JWT for authentication"
        }

        claims = validator._extract_claims(adr)

        assert len(claims) == 2
        assert claims[0]['type'] == 'coverage'
        assert claims[1]['type'] == 'technology'

    def test_empty_adr_list(self, validator, tmp_path):
        """Test validation with no ADRs"""
        result = validator.validate(tmp_path, [])

        assert result['summary']['total_adrs'] == 0
        assert result['summary']['total_claims'] == 0
        assert result['summary']['validation_rate'] == 0

    def test_adr_without_claims(self, validator, tmp_path):
        """Test ADR that makes no validatable claims"""
        adr = {
            "id": "ADR-004",
            "title": "Use PostgreSQL",
            "decision": "We chose PostgreSQL as our database"
        }

        result = validator.validate(tmp_path, [adr])

        adr_result = result['results'][0]
        assert adr_result['claims_count'] == 0
        assert adr_result['validated_count'] == 0

    def test_disabled_validation(self, tmp_path):
        """Test that disabled validation skips processing"""
        config = {"adr_validation": {"enabled": False}}
        validator = ADRValidator(config)
        assert validator.enabled is False

    def test_validation_summary_statistics(self, validator, tmp_path):
        """Test overall validation statistics"""
        # Create RLS implementation
        migration_file = tmp_path / "Migrations" / "AddRLS.cs"
        migration_file.parent.mkdir(parents=True)
        migration_file.write_text("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")

        # Multiple ADRs with claims
        adrs = [
            {
                "id": "ADR-001",
                "decision": "Uses Row-Level Security"
            },
            {
                "id": "ADR-002",
                "decision": "LGPD coverage 50%"  # Will fail (no implementation)
            }
        ]

        result = validator.validate(tmp_path, adrs)

        assert result['summary']['total_adrs'] == 2
        assert result['summary']['total_claims'] == 2
        # One claim valid, one invalid = 50% rate
        assert 0 < result['summary']['validation_rate'] < 1

    def test_tolerance_percentage(self, validator, tmp_path):
        """Test that tolerance percentage is respected"""
        # Create 7/8 LGPD methods = 87.5% coverage
        lgpd_file = tmp_path / "Services" / "DataSubjectRightService.cs"
        lgpd_file.parent.mkdir(parents=True)
        lgpd_file.write_text("""
            public class DataSubjectRightService {
                public void RequestDataDeletion() {}
                public void RequestDataPortability() {}
                public void RevokeConsent() {}
                public void RequestDataAccess() {}
                public void RequestDataRectification() {}
                public void RequestDataAnonymization() {}
                public void RequestDataOpposition() {}
            }
        """)

        # Claim 90% (within 10% tolerance of 87.5%)
        adr = {
            "id": "ADR-001",
            "decision": "LGPD coverage 90%"
        }

        result = validator.validate(tmp_path, [adr])
        claim_result = result['results'][0]['claims'][0]

        # Should be valid because within tolerance
        assert claim_result['is_valid'] is True

    def test_evidence_file_tracking(self, validator, tmp_path):
        """Test that evidence files are properly tracked"""
        # Create multiple files with RLS
        for i in range(3):
            migration_file = tmp_path / "Migrations" / f"Migration{i}.cs"
            migration_file.parent.mkdir(parents=True, exist_ok=True)
            migration_file.write_text(f"CREATE POLICY policy_{i};")

        adr = {
            "id": "ADR-001",
            "decision": "Uses Row-Level Security"
        }

        result = validator.validate(tmp_path, [adr])
        claim_result = result['results'][0]['claims'][0]

        assert 'evidence_files' in claim_result
        assert len(claim_result['evidence_files']) == 3
