#!/usr/bin/env python3
"""
Test script to reproduce the workflow execution issue.
"""


def test_workflow_definition_query_logic():
    """Test the difference between list and get query logic."""
    
    # Mock scenarios - the actual issue
    scenarios = [
        {
            "name": "User owns workflow, is_public=False",
            "workflow": {"owner_id": "user123", "is_public": False},
            "query_user": "user123",
            "should_list": True,
            "should_get": True,
        },
        {
            "name": "User owns workflow, is_public=True", 
            "workflow": {"owner_id": "user123", "is_public": True},
            "query_user": "user123",
            "should_list": True,
            "should_get": True,
        },
        {
            "name": "User doesn't own workflow, is_public=True",
            "workflow": {"owner_id": "other_user", "is_public": True},
            "query_user": "user123",
            "should_list": True,
            "should_get": True,
        },
        {
            "name": "User doesn't own workflow, is_public=False", 
            "workflow": {"owner_id": "other_user", "is_public": False},
            "query_user": "user123",
            "should_list": False,
            "should_get": False,
        },
        {
            "name": "User doesn't own workflow, is_public=None (NULL)",
            "workflow": {"owner_id": "other_user", "is_public": None},
            "query_user": "user123", 
            "should_list": False,
            "should_get": False,
        },
        {
            "name": "PROBLEMATIC: User doesn't own workflow, is_public=1 (truthy but not True)",
            "workflow": {"owner_id": "other_user", "is_public": 1},
            "query_user": "user123", 
            "should_list": False,  # Should NOT be listed
            "should_get": False,   # Should NOT be retrievable
        },
    ]
    
    print("Testing workflow query logic consistency...")
    print("=" * 60)
    
    for scenario in scenarios:
        print(f"\nScenario: {scenario['name']}")
        print(f"  Workflow: owner_id={scenario['workflow']['owner_id']}, is_public={scenario['workflow']['is_public']}")
        print(f"  Query user: {scenario['query_user']}")
        
        # Simulate OLD list_workflow_definitions logic (BUGGY)
        owner_condition = scenario['workflow']['owner_id'] == scenario['query_user']
        old_public_condition = bool(scenario['workflow']['is_public'])  # Truthy check - WRONG!
        old_list_result = owner_condition or old_public_condition
        
        # Simulate OLD get_workflow_definition logic (BUGGY)  
        old_get_result = owner_condition or bool(scenario['workflow']['is_public'])  # Truthy check - WRONG!
        
        # Simulate NEW FIXED logic
        new_public_condition = scenario['workflow']['is_public'] is True  # Explicit True check - CORRECT!
        new_list_result = owner_condition or new_public_condition
        new_get_result = owner_condition or new_public_condition
        
        print(f"  OLD List query result: {old_list_result}")
        print(f"  OLD Get query result: {old_get_result}")
        print(f"  NEW List query result: {new_list_result} (expected: {scenario['should_list']})")
        print(f"  NEW Get query result: {new_get_result} (expected: {scenario['should_get']})")
        
        old_list_match = old_list_result == scenario['should_list']
        old_get_match = old_get_result == scenario['should_get']
        old_consistency = old_list_result == old_get_result
        
        new_list_match = new_list_result == scenario['should_list']
        new_get_match = new_get_result == scenario['should_get']
        new_consistency = new_list_result == new_get_result
        
        print(f"  OLD: List correct: {old_list_match}, Get correct: {old_get_match}, Consistent: {old_consistency}")
        print(f"  NEW: List correct: {new_list_match}, Get correct: {new_get_match}, Consistent: {new_consistency}")
        
        if not new_list_match or not new_get_match or not new_consistency:
            print(f"  ❌ STILL HAS ISSUES!")
        elif not old_list_match or not old_get_match or not old_consistency:
            print(f"  ✅ FIXED!")
        else:
            print(f"  ✅ OK")


if __name__ == "__main__":
    test_workflow_definition_query_logic()