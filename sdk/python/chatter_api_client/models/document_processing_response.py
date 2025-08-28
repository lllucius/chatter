import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.document_status import DocumentStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentProcessingResponse")


@_attrs_define
class DocumentProcessingResponse:
    """Schema for document processing response.

    Attributes:
        document_id (str): Document ID
        status (DocumentStatus): Enumeration for document processing status.
        message (str): Status message
        processing_started_at (Union[None, Unset, datetime.datetime]): Processing start time
    """

    document_id: str
    status: DocumentStatus
    message: str
    processing_started_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document_id = self.document_id

        status = self.status.value

        message = self.message

        processing_started_at: Union[None, Unset, str]
        if isinstance(self.processing_started_at, Unset):
            processing_started_at = UNSET
        elif isinstance(self.processing_started_at, datetime.datetime):
            processing_started_at = self.processing_started_at.isoformat()
        else:
            processing_started_at = self.processing_started_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document_id": document_id,
                "status": status,
                "message": message,
            }
        )
        if processing_started_at is not UNSET:
            field_dict["processing_started_at"] = processing_started_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_id = d.pop("document_id")

        status = DocumentStatus(d.pop("status"))

        message = d.pop("message")

        def _parse_processing_started_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                processing_started_at_type_0 = isoparse(data)

                return processing_started_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        processing_started_at = _parse_processing_started_at(d.pop("processing_started_at", UNSET))

        document_processing_response = cls(
            document_id=document_id,
            status=status,
            message=message,
            processing_started_at=processing_started_at,
        )

        document_processing_response.additional_properties = d
        return document_processing_response

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
