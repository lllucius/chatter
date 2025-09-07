# TokenResponse

Schema for authentication token response.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**access_token** | **str** | JWT access token | 
**refresh_token** | **str** | JWT refresh token | 
**token_type** | **str** | Token type | [optional] [default to 'bearer']
**expires_in** | **int** | Token expiration time in seconds | 
**user** | [**UserResponse**](UserResponse.md) |  | 

## Example

```python
from chatter_sdk.models.token_response import TokenResponse

# TODO update the JSON string below
json = "{}"
# create an instance of TokenResponse from a JSON string
token_response_instance = TokenResponse.from_json(json)
# print the JSON string representation of the object
print(TokenResponse.to_json())

# convert the object into a dict
token_response_dict = token_response_instance.to_dict()
# create an instance of TokenResponse from a dict
token_response_from_dict = TokenResponse.from_dict(token_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


