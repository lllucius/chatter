import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.data_format import DataFormat
from ..models.export_scope import ExportScope
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.export_data_request_custom_query_type_0 import ExportDataRequestCustomQueryType0


T = TypeVar("T", bound="ExportDataRequest")


@_attrs_define
class ExportDataRequest:
    """Request schema for data export API.

    Attributes:
        scope (ExportScope): Data export scope.
        format_ (Union[Unset, DataFormat]): Supported data formats.
        user_id (Union[None, Unset, str]): Filter by user ID
        conversation_id (Union[None, Unset, str]): Filter by conversation ID
        date_from (Union[None, Unset, datetime.datetime]): Filter from date
        date_to (Union[None, Unset, datetime.datetime]): Filter to date
        include_metadata (Union[Unset, bool]): Include metadata Default: True.
        compress (Union[Unset, bool]): Compress export file Default: True.
        encrypt (Union[Unset, bool]): Encrypt export file Default: False.
        custom_query (Union['ExportDataRequestCustomQueryType0', None, Unset]): Custom export query
    """

    scope: ExportScope
    format_: Union[Unset, DataFormat] = UNSET
    user_id: Union[None, Unset, str] = UNSET
    conversation_id: Union[None, Unset, str] = UNSET
    date_from: Union[None, Unset, datetime.datetime] = UNSET
    date_to: Union[None, Unset, datetime.datetime] = UNSET
    include_metadata: Union[Unset, bool] = True
    compress: Union[Unset, bool] = True
    encrypt: Union[Unset, bool] = False
    custom_query: Union["ExportDataRequestCustomQueryType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.export_data_request_custom_query_type_0 import ExportDataRequestCustomQueryType0

        scope = self.scope.value

        format_: Union[Unset, str] = UNSET
        if not isinstance(self.format_, Unset):
            format_ = self.format_.value

        user_id: Union[None, Unset, str]
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        conversation_id: Union[None, Unset, str]
        if isinstance(self.conversation_id, Unset):
            conversation_id = UNSET
        else:
            conversation_id = self.conversation_id

        date_from: Union[None, Unset, str]
        if isinstance(self.date_from, Unset):
            date_from = UNSET
        elif isinstance(self.date_from, datetime.datetime):
            date_from = self.date_from.isoformat()
        else:
            date_from = self.date_from

        date_to: Union[None, Unset, str]
        if isinstance(self.date_to, Unset):
            date_to = UNSET
        elif isinstance(self.date_to, datetime.datetime):
            date_to = self.date_to.isoformat()
        else:
            date_to = self.date_to

        include_metadata = self.include_metadata

        compress = self.compress

        encrypt = self.encrypt

        custom_query: Union[None, Unset, dict[str, Any]]
        if isinstance(self.custom_query, Unset):
            custom_query = UNSET
        elif isinstance(self.custom_query, ExportDataRequestCustomQueryType0):
            custom_query = self.custom_query.to_dict()
        else:
            custom_query = self.custom_query

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scope": scope,
            }
        )
        if format_ is not UNSET:
            field_dict["format"] = format_
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if conversation_id is not UNSET:
            field_dict["conversation_id"] = conversation_id
        if date_from is not UNSET:
            field_dict["date_from"] = date_from
        if date_to is not UNSET:
            field_dict["date_to"] = date_to
        if include_metadata is not UNSET:
            field_dict["include_metadata"] = include_metadata
        if compress is not UNSET:
            field_dict["compress"] = compress
        if encrypt is not UNSET:
            field_dict["encrypt"] = encrypt
        if custom_query is not UNSET:
            field_dict["custom_query"] = custom_query

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.export_data_request_custom_query_type_0 import ExportDataRequestCustomQueryType0

        d = dict(src_dict)
        scope = ExportScope(d.pop("scope"))

        _format_ = d.pop("format", UNSET)
        format_: Union[Unset, DataFormat]
        if isinstance(_format_, Unset):
            format_ = UNSET
        else:
            format_ = DataFormat(_format_)

        def _parse_user_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user_id = _parse_user_id(d.pop("user_id", UNSET))

        def _parse_conversation_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        conversation_id = _parse_conversation_id(d.pop("conversation_id", UNSET))

        def _parse_date_from(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                date_from_type_0 = isoparse(data)

                return date_from_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        date_from = _parse_date_from(d.pop("date_from", UNSET))

        def _parse_date_to(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                date_to_type_0 = isoparse(data)

                return date_to_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        date_to = _parse_date_to(d.pop("date_to", UNSET))

        include_metadata = d.pop("include_metadata", UNSET)

        compress = d.pop("compress", UNSET)

        encrypt = d.pop("encrypt", UNSET)

        def _parse_custom_query(data: object) -> Union["ExportDataRequestCustomQueryType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_query_type_0 = ExportDataRequestCustomQueryType0.from_dict(data)

                return custom_query_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ExportDataRequestCustomQueryType0", None, Unset], data)

        custom_query = _parse_custom_query(d.pop("custom_query", UNSET))

        export_data_request = cls(
            scope=scope,
            format_=format_,
            user_id=user_id,
            conversation_id=conversation_id,
            date_from=date_from,
            date_to=date_to,
            include_metadata=include_metadata,
            compress=compress,
            encrypt=encrypt,
            custom_query=custom_query,
        )

        export_data_request.additional_properties = d
        return export_data_request

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
