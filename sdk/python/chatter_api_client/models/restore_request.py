from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.restore_request_restore_options import RestoreRequestRestoreOptions


T = TypeVar("T", bound="RestoreRequest")


@_attrs_define
class RestoreRequest:
    """Request schema for restoring from backup.

    Attributes:
        backup_id (str): Backup ID to restore from
        restore_options (Union[Unset, RestoreRequestRestoreOptions]): Restore options
        create_backup_before_restore (Union[Unset, bool]): Create backup before restore Default: True.
        verify_integrity (Union[Unset, bool]): Verify backup integrity before restore Default: True.
    """

    backup_id: str
    restore_options: Union[Unset, "RestoreRequestRestoreOptions"] = UNSET
    create_backup_before_restore: Union[Unset, bool] = True
    verify_integrity: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        backup_id = self.backup_id

        restore_options: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.restore_options, Unset):
            restore_options = self.restore_options.to_dict()

        create_backup_before_restore = self.create_backup_before_restore

        verify_integrity = self.verify_integrity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "backup_id": backup_id,
            }
        )
        if restore_options is not UNSET:
            field_dict["restore_options"] = restore_options
        if create_backup_before_restore is not UNSET:
            field_dict["create_backup_before_restore"] = create_backup_before_restore
        if verify_integrity is not UNSET:
            field_dict["verify_integrity"] = verify_integrity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.restore_request_restore_options import RestoreRequestRestoreOptions

        d = dict(src_dict)
        backup_id = d.pop("backup_id")

        _restore_options = d.pop("restore_options", UNSET)
        restore_options: Union[Unset, RestoreRequestRestoreOptions]
        if isinstance(_restore_options, Unset):
            restore_options = UNSET
        else:
            restore_options = RestoreRequestRestoreOptions.from_dict(_restore_options)

        create_backup_before_restore = d.pop("create_backup_before_restore", UNSET)

        verify_integrity = d.pop("verify_integrity", UNSET)

        restore_request = cls(
            backup_id=backup_id,
            restore_options=restore_options,
            create_backup_before_restore=create_backup_before_restore,
            verify_integrity=verify_integrity,
        )

        restore_request.additional_properties = d
        return restore_request

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
