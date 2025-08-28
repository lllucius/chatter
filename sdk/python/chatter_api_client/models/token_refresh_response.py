from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TokenRefreshResponse")


@_attrs_define
class TokenRefreshResponse:
    """Schema for token refresh response.

    Attributes:
        access_token (str): New access token
        refresh_token (str): New refresh token
        expires_in (int): Token expiration time in seconds
        token_type (Union[Unset, str]): Token type Default: 'bearer'.
    """

    access_token: str
    refresh_token: str
    expires_in: int
    token_type: Union[Unset, str] = "bearer"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token = self.access_token

        refresh_token = self.refresh_token

        expires_in = self.expires_in

        token_type = self.token_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
            }
        )
        if token_type is not UNSET:
            field_dict["token_type"] = token_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        access_token = d.pop("access_token")

        refresh_token = d.pop("refresh_token")

        expires_in = d.pop("expires_in")

        token_type = d.pop("token_type", UNSET)

        token_refresh_response = cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            token_type=token_type,
        )

        token_refresh_response.additional_properties = d
        return token_refresh_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
