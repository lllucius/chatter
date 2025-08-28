from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.profile_test_response_retrieval_results_type_0_item import (
        ProfileTestResponseRetrievalResultsType0Item,
    )
    from ..models.profile_test_response_usage_info import ProfileTestResponseUsageInfo


T = TypeVar("T", bound="ProfileTestResponse")


@_attrs_define
class ProfileTestResponse:
    """Schema for profile test response.

    Attributes:
        profile_id (str): Profile ID
        test_message (str): Test message sent
        response (str): Generated response
        usage_info (ProfileTestResponseUsageInfo): Token usage and cost information
        response_time_ms (int): Response time in milliseconds
        retrieval_results (Union[None, Unset, list['ProfileTestResponseRetrievalResultsType0Item']]): Retrieval results
            if enabled
        tools_used (Union[None, Unset, list[str]]): Tools used if enabled
    """

    profile_id: str
    test_message: str
    response: str
    usage_info: "ProfileTestResponseUsageInfo"
    response_time_ms: int
    retrieval_results: Union[None, Unset, list["ProfileTestResponseRetrievalResultsType0Item"]] = UNSET
    tools_used: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        profile_id = self.profile_id

        test_message = self.test_message

        response = self.response

        usage_info = self.usage_info.to_dict()

        response_time_ms = self.response_time_ms

        retrieval_results: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.retrieval_results, Unset):
            retrieval_results = UNSET
        elif isinstance(self.retrieval_results, list):
            retrieval_results = []
            for retrieval_results_type_0_item_data in self.retrieval_results:
                retrieval_results_type_0_item = retrieval_results_type_0_item_data.to_dict()
                retrieval_results.append(retrieval_results_type_0_item)

        else:
            retrieval_results = self.retrieval_results

        tools_used: Union[None, Unset, list[str]]
        if isinstance(self.tools_used, Unset):
            tools_used = UNSET
        elif isinstance(self.tools_used, list):
            tools_used = self.tools_used

        else:
            tools_used = self.tools_used

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "profile_id": profile_id,
                "test_message": test_message,
                "response": response,
                "usage_info": usage_info,
                "response_time_ms": response_time_ms,
            }
        )
        if retrieval_results is not UNSET:
            field_dict["retrieval_results"] = retrieval_results
        if tools_used is not UNSET:
            field_dict["tools_used"] = tools_used

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_test_response_retrieval_results_type_0_item import (
            ProfileTestResponseRetrievalResultsType0Item,
        )
        from ..models.profile_test_response_usage_info import ProfileTestResponseUsageInfo

        d = dict(src_dict)
        profile_id = d.pop("profile_id")

        test_message = d.pop("test_message")

        response = d.pop("response")

        usage_info = ProfileTestResponseUsageInfo.from_dict(d.pop("usage_info"))

        response_time_ms = d.pop("response_time_ms")

        def _parse_retrieval_results(
            data: object,
        ) -> Union[None, Unset, list["ProfileTestResponseRetrievalResultsType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                retrieval_results_type_0 = []
                _retrieval_results_type_0 = data
                for retrieval_results_type_0_item_data in _retrieval_results_type_0:
                    retrieval_results_type_0_item = ProfileTestResponseRetrievalResultsType0Item.from_dict(
                        retrieval_results_type_0_item_data
                    )

                    retrieval_results_type_0.append(retrieval_results_type_0_item)

                return retrieval_results_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["ProfileTestResponseRetrievalResultsType0Item"]], data)

        retrieval_results = _parse_retrieval_results(d.pop("retrieval_results", UNSET))

        def _parse_tools_used(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tools_used_type_0 = cast(list[str], data)

                return tools_used_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        tools_used = _parse_tools_used(d.pop("tools_used", UNSET))

        profile_test_response = cls(
            profile_id=profile_id,
            test_message=test_message,
            response=response,
            usage_info=usage_info,
            response_time_ms=response_time_ms,
            retrieval_results=retrieval_results,
            tools_used=tools_used,
        )

        profile_test_response.additional_properties = d
        return profile_test_response

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
