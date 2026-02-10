#!/usr/bin/env python3
"""
Design validation utilities for SDLC Agêntico Phase 4 (Design System & UX)
Validates design tokens, accessibility compliance, and component specifications.
Cross-platform compatible (Linux + Windows).
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple

def validate_tokens(tokens_file: str) -> Tuple[bool, str]:
    """Validate design tokens YAML structure and syntax."""
    try:
        tokens_path = Path(tokens_file)
        if not tokens_path.exists():
            return False, f"❌ Tokens file not found: {tokens_file}"
        
        with open(tokens_path, 'r', encoding='utf-8') as f:
            tokens = yaml.safe_load(f)
        
        # Check required categories
        required_categories = ['color', 'spacing', 'typography', 'border', 'shadow']
        missing = [cat for cat in required_categories if cat not in tokens]
        
        if missing:
            return False, f"❌ Missing required token categories: {', '.join(missing)}"
        
        # Validate color tokens have hex values
        colors = tokens.get('color', {})
        for key, value in colors.items():
            if isinstance(value, dict) and 'value' in value:
                color_val = value['value']
                if not re.match(r'^#[0-9A-Fa-f]{6}$', color_val):
                    return False, f"❌ Invalid hex color: {key} = {color_val}"
        
        return True, "✅ Design tokens valid"
    
    except yaml.YAMLError as e:
        return False, f"❌ YAML syntax error: {e}"
    except Exception as e:
        return False, f"❌ Validation error: {e}"

def check_accessibility(design_dir: str) -> Tuple[bool, str]:
    """Basic accessibility validation."""
    try:
        design_path = Path(design_dir)
        if not design_path.exists():
            return False, f"❌ Design directory not found: {design_dir}"
        
        # Check if accessibility checklist exists
        a11y_file = design_path / "accessibility-checklist.md"
        if not a11y_file.exists():
            return False, "❌ Accessibility checklist not found"
        
        # Basic content check
        content = a11y_file.read_text(encoding='utf-8')
        required_sections = ['Color & Contrast', 'Keyboard Navigation', 'Screen Reader']
        missing = [section for section in required_sections if section not in content]
        
        if missing:
            return False, f"⚠️ Missing a11y sections: {', '.join(missing)}"
        
        return True, "✅ Accessibility checklist complete"
    
    except Exception as e:
        return False, f"❌ A11y check error: {e}"

def lint_components(components_dir: str) -> Tuple[bool, str]:
    """Validate component specifications completeness."""
    try:
        comp_path = Path(components_dir)
        if not comp_path.exists():
            return False, f"❌ Components directory not found: {components_dir}"
        
        # Count component spec files
        spec_files = list(comp_path.glob("*.md"))
        if len(spec_files) < 5:
            return False, f"❌ Only {len(spec_files)} component specs found (minimum 5 required)"
        
        # Check each spec has required sections
        for spec_file in spec_files:
            content = spec_file.read_text(encoding='utf-8')
            required_sections = ['## Purpose', '## API Specification', '## States', '## Accessibility']
            missing = [section for section in required_sections if section not in content]
            
            if missing:
                return False, f"⚠️ {spec_file.name} missing sections: {', '.join(missing)}"
        
        return True, f"✅ Component specs complete ({len(spec_files)} components)"
    
    except Exception as e:
        return False, f"❌ Component lint error: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: design_validation.py <command> [args]")
        print("Commands:")
        print("  validate-tokens <tokens.yml>")
        print("  check-accessibility <design_dir>")
        print("  lint-components <components_dir>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "validate-tokens" and len(sys.argv) == 3:
        success, message = validate_tokens(sys.argv[2])
        print(message)
        sys.exit(0 if success else 1)
    
    elif command == "check-accessibility" and len(sys.argv) == 3:
        success, message = check_accessibility(sys.argv[2])
        print(message)
        sys.exit(0 if success else 1)
    
    elif command == "lint-components" and len(sys.argv) == 3:
        success, message = lint_components(sys.argv[2])
        print(message)
        sys.exit(0 if success else 1)
    
    else:
        print(f"❌ Unknown command or invalid arguments: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
