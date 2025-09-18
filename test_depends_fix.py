"""Test to demonstrate the Depends() issue with GET endpoints."""

import pytest
from fastapi import FastAPI, Depends, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class TestType(str, Enum):
    TYPE1 = "type1"
    TYPE2 = "type2"


class TestListRequest(BaseModel):
    """Test request model with optional filters."""
    
    filter_type: Optional[TestType] = Field(None, description="Filter by type")
    status: Optional[str] = Field(None, description="Filter by status")
    enabled: Optional[bool] = Field(None, description="Filter by enabled status")


# Incorrect pattern - this may work but is not the FastAPI recommended approach
app_incorrect = FastAPI()

@app_incorrect.get("/test-incorrect")
async def test_incorrect_endpoint(
    request: TestListRequest = Depends(),  # This is not the recommended pattern
):
    return {"request": request.model_dump()}


# Correct pattern - individual query parameters 
app_correct = FastAPI()

@app_correct.get("/test-correct")
async def test_correct_endpoint(
    filter_type: Optional[TestType] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
):
    return {"filter_type": filter_type, "status": status, "enabled": enabled}


# Alternative correct pattern - dependency function
def get_test_request(
    filter_type: Optional[TestType] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled status"),
) -> TestListRequest:
    """Create TestListRequest from query parameters."""
    return TestListRequest(
        filter_type=filter_type,
        status=status,
        enabled=enabled
    )


app_alternative = FastAPI()

@app_alternative.get("/test-alternative")
async def test_alternative_endpoint(
    request: TestListRequest = Depends(get_test_request),
):
    return {"request": request.model_dump()}


def test_patterns():
    """Test all patterns to see differences."""
    
    # Test the patterns that might be problematic
    client_incorrect = TestClient(app_incorrect)
    client_correct = TestClient(app_correct)
    client_alternative = TestClient(app_alternative)
    
    query_params = "?filter_type=type1&status=active&enabled=true"
    
    # Test incorrect pattern
    response1 = client_incorrect.get(f"/test-incorrect{query_params}")
    print(f"Incorrect pattern response: {response1.json()}")
    print(f"Status code: {response1.status_code}")
    
    # Test correct pattern
    response2 = client_correct.get(f"/test-correct{query_params}")
    print(f"Correct pattern response: {response2.json()}")
    print(f"Status code: {response2.status_code}")
    
    # Test alternative pattern
    response3 = client_alternative.get(f"/test-alternative{query_params}")
    print(f"Alternative pattern response: {response3.json()}")
    print(f"Status code: {response3.status_code}")
    
    # Test edge cases
    print("\n--- Testing edge cases ---")
    
    # Test with no parameters
    response_empty = client_incorrect.get("/test-incorrect")
    print(f"No params - incorrect: {response_empty.json()}")
    
    # Test with invalid enum value
    response_invalid = client_incorrect.get("/test-incorrect?filter_type=invalid&status=test")
    print(f"Invalid enum - incorrect: {response_invalid.status_code}")
    if response_invalid.status_code != 200:
        print(f"Error response: {response_invalid.json()}")


if __name__ == "__main__":
    test_patterns()