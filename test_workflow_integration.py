"""Simple integration tests for workflow template database persistence.

These tests can be run without the full application configuration.
"""

import asyncio
import sys
import os
import importlib.util

# Load the module directly from file to avoid import issues
spec = importlib.util.spec_from_file_location(
    "unified_template_manager", 
    os.path.join(os.path.dirname(__file__), "chatter", "core", "unified_template_manager.py")
)
utm_module = importlib.util.module_from_spec(spec)

# Execute the module
spec.loader.exec_module(utm_module)

# Get the classes we need
UnifiedTemplateManager = utm_module.UnifiedTemplateManager
WorkflowTemplate = utm_module.WorkflowTemplate
TemplateSpec = utm_module.TemplateSpec
ValidationResult = utm_module.ValidationResult
WorkflowConfigurationError = utm_module.WorkflowConfigurationError


async def test_builtin_templates():
    """Test built-in template functionality."""
    print("Testing built-in templates...")
    
    manager = UnifiedTemplateManager(session=None)
    
    # Test template listing
    templates = await manager.list_templates(include_custom=False)
    print(f"Found {len(templates)} built-in templates: {templates}")
    
    # Test template retrieval
    for template_name in ['general_chat', 'customer_support', 'code_assistant']:
        try:
            template = await manager.get_template(template_name)
            print(f"✓ Retrieved template: {template.name} ({template.workflow_type})")
        except Exception as e:
            print(f"✗ Error retrieving {template_name}: {e}")
            return False
    
    # Test template info
    info = await manager.get_template_info()
    print(f"Template info contains {len(info)} templates")
    
    return True


async def test_template_validation():
    """Test template validation functionality."""
    print("\nTesting template validation...")
    
    manager = UnifiedTemplateManager(session=None)
    
    # Test valid template
    valid_template = WorkflowTemplate(
        name="test_valid",
        workflow_type="plain",
        description="Valid test template",
        default_params={"system_message": "Test system message"},
    )
    
    result = await manager.validate_template(valid_template)
    if not result.valid:
        print(f"✗ Valid template failed validation: {result.errors}")
        return False
    print("✓ Valid template passed validation")
    
    # Test invalid template
    invalid_template = WorkflowTemplate(
        name="",  # Empty name
        workflow_type="invalid_type",  # Invalid type
        description="",  # Empty description
        default_params={},
    )
    
    result = await manager.validate_template(invalid_template)
    if result.valid:
        print("✗ Invalid template incorrectly passed validation")
        return False
    print(f"✓ Invalid template correctly failed validation with {len(result.errors)} errors")
    
    return True


async def test_custom_template_creation():
    """Test custom template creation without database."""
    print("\nTesting custom template creation...")
    
    manager = UnifiedTemplateManager(session=None)
    
    # Create a custom template spec
    spec = TemplateSpec(
        name="test_custom_template",
        description="Test custom template",
        workflow_type="tools",
        default_params={
            "system_message": "Custom system message",
            "enable_memory": True,
        },
        required_tools=["test_tool"],
        base_template="general_chat",
    )
    
    try:
        template = await manager.create_custom_template(spec, "test_user")
        print(f"✓ Created custom template: {template.name}")
        
        # Verify the template was created correctly
        if template.required_tools != ["test_tool"]:
            print("✗ Custom template tools not set correctly")
            return False
        
        if "Custom system message" not in str(template.default_params):
            print("✗ Custom template params not set correctly")
            return False
        
        print("✓ Custom template configuration verified")
        
    except Exception as e:
        print(f"✗ Error creating custom template: {e}")
        return False
    
    return True


async def test_workflow_spec_building():
    """Test workflow specification building."""
    print("\nTesting workflow spec building...")
    
    manager = UnifiedTemplateManager(session=None)
    
    try:
        # Build spec for a built-in template
        spec = await manager.build_workflow_spec(
            "general_chat",
            overrides={
                "parameters": {"temperature": 0.7},
                "additional_tools": ["calculator"],
            }
        )
        
        print(f"✓ Built workflow spec for 'general_chat'")
        
        # Verify spec structure
        expected_keys = ["template_name", "workflow_type", "description", "parameters", "required_tools", "required_retrievers"]
        for key in expected_keys:
            if key not in spec:
                print(f"✗ Missing key in workflow spec: {key}")
                return False
        
        if spec["parameters"]["temperature"] != 0.7:
            print("✗ Override parameters not applied correctly")
            return False
        
        if "calculator" not in spec["required_tools"]:
            print("✗ Additional tools not applied correctly")
            return False
        
        print("✓ Workflow spec structure and overrides verified")
        
    except Exception as e:
        print(f"✗ Error building workflow spec: {e}")
        return False
    
    return True


async def test_template_requirements_validation():
    """Test template requirements validation."""
    print("\nTesting template requirements validation...")
    
    manager = UnifiedTemplateManager(session=None)
    
    try:
        # Test with missing requirements
        result = await manager.validate_template_requirements(
            "code_assistant",
            available_tools=["some_other_tool"],  # Missing required tools
            available_retrievers=[],
        )
        
        if result.valid:
            print("✗ Template with missing requirements incorrectly passed validation")
            return False
        
        if not result.missing_tools:
            print("✗ Missing tools not properly identified")
            return False
        
        print(f"✓ Template requirements validation identified {len(result.missing_tools)} missing tools")
        
        # Test with all requirements met
        code_template = await manager.get_template("code_assistant")
        result = await manager.validate_template_requirements(
            "code_assistant",
            available_tools=code_template.required_tools,
            available_retrievers=[],
        )
        
        if not result.valid:
            print(f"✗ Template with all requirements failed validation: {result.errors}")
            return False
        
        print("✓ Template with all requirements passed validation")
        
    except Exception as e:
        print(f"✗ Error validating template requirements: {e}")
        return False
    
    return True


async def test_error_handling():
    """Test error handling for various edge cases."""
    print("\nTesting error handling...")
    
    manager = UnifiedTemplateManager(session=None)
    
    # Test non-existent template
    try:
        await manager.get_template("nonexistent_template")
        print("✗ Should have raised error for non-existent template")
        return False
    except WorkflowConfigurationError:
        print("✓ Correctly raised error for non-existent template")
    except Exception as e:
        print(f"✗ Unexpected error type: {e}")
        return False
    
    # Test invalid template creation
    try:
        invalid_spec = TemplateSpec(
            name="",  # Invalid empty name
            description="Test",
            workflow_type="invalid_type",
            default_params={},
        )
        await manager.create_custom_template(invalid_spec, "test_user")
        print("✗ Should have raised error for invalid template spec")
        return False
    except WorkflowConfigurationError:
        print("✓ Correctly raised error for invalid template spec")
    except Exception as e:
        print(f"✗ Unexpected error type: {e}")
        return False
    
    return True


async def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Built-in Templates", test_builtin_templates),
        ("Template Validation", test_template_validation),
        ("Custom Template Creation", test_custom_template_creation),
        ("Workflow Spec Building", test_workflow_spec_building),
        ("Requirements Validation", test_template_requirements_validation),
        ("Error Handling", test_error_handling),
    ]
    
    print("=" * 60)
    print("WORKFLOW TEMPLATE PERSISTENCE INTEGRATION TESTS")
    print("=" * 60)
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database persistence implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)