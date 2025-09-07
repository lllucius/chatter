# OAuthConfigSchema

OAuth configuration for remote servers.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**client_id** | **str** | OAuth client ID | 
**client_secret** | **str** | OAuth client secret | 
**token_url** | **str** | OAuth token endpoint URL | 
**scope** | **str** |  | [optional] 

## Example

```python
from chatter_sdk.models.o_auth_config_schema import OAuthConfigSchema

# TODO update the JSON string below
json = "{}"
# create an instance of OAuthConfigSchema from a JSON string
o_auth_config_schema_instance = OAuthConfigSchema.from_json(json)
# print the JSON string representation of the object
print(OAuthConfigSchema.to_json())

# convert the object into a dict
o_auth_config_schema_dict = o_auth_config_schema_instance.to_dict()
# create an instance of OAuthConfigSchema from a dict
o_auth_config_schema_from_dict = OAuthConfigSchema.from_dict(o_auth_config_schema_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


