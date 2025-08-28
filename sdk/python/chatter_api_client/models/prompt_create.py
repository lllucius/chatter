from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.prompt_category import PromptCategory
from ..models.prompt_type import PromptType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prompt_create_chain_steps_type_0_item import PromptCreateChainStepsType0Item
    from ..models.prompt_create_examples_type_0_item import PromptCreateExamplesType0Item
    from ..models.prompt_create_extra_metadata_type_0 import PromptCreateExtraMetadataType0
    from ..models.prompt_create_input_schema_type_0 import PromptCreateInputSchemaType0
    from ..models.prompt_create_output_schema_type_0 import PromptCreateOutputSchemaType0
    from ..models.prompt_create_test_cases_type_0_item import PromptCreateTestCasesType0Item


T = TypeVar("T", bound="PromptCreate")


@_attrs_define
class PromptCreate:
    """Schema for creating a prompt.

    Attributes:
        name (str): Prompt name
        content (str): Prompt content/template
        description (Union[None, Unset, str]): Prompt description
        prompt_type (Union[Unset, PromptType]): Enumeration for prompt types.
        category (Union[Unset, PromptCategory]): Enumeration for prompt categories.
        variables (Union[None, Unset, list[str]]): Template variables
        template_format (Union[Unset, str]): Template format (f-string, jinja2, mustache) Default: 'f-string'.
        input_schema (Union['PromptCreateInputSchemaType0', None, Unset]): JSON schema for input validation
        output_schema (Union['PromptCreateOutputSchemaType0', None, Unset]): JSON schema for output validation
        max_length (Union[None, Unset, int]): Maximum content length
        min_length (Union[None, Unset, int]): Minimum content length
        required_variables (Union[None, Unset, list[str]]): Required template variables
        examples (Union[None, Unset, list['PromptCreateExamplesType0Item']]): Usage examples
        test_cases (Union[None, Unset, list['PromptCreateTestCasesType0Item']]): Test cases
        suggested_temperature (Union[None, Unset, float]): Suggested temperature
        suggested_max_tokens (Union[None, Unset, int]): Suggested max tokens
        suggested_providers (Union[None, Unset, list[str]]): Suggested LLM providers
        is_chain (Union[Unset, bool]): Whether this is a chain prompt Default: False.
        chain_steps (Union[None, Unset, list['PromptCreateChainStepsType0Item']]): Chain execution steps
        parent_prompt_id (Union[None, Unset, str]): Parent prompt ID for chains
        is_public (Union[Unset, bool]): Whether prompt is public Default: False.
        tags (Union[None, Unset, list[str]]): Prompt tags
        extra_metadata (Union['PromptCreateExtraMetadataType0', None, Unset]): Additional metadata
    """

    name: str
    content: str
    description: Union[None, Unset, str] = UNSET
    prompt_type: Union[Unset, PromptType] = UNSET
    category: Union[Unset, PromptCategory] = UNSET
    variables: Union[None, Unset, list[str]] = UNSET
    template_format: Union[Unset, str] = "f-string"
    input_schema: Union["PromptCreateInputSchemaType0", None, Unset] = UNSET
    output_schema: Union["PromptCreateOutputSchemaType0", None, Unset] = UNSET
    max_length: Union[None, Unset, int] = UNSET
    min_length: Union[None, Unset, int] = UNSET
    required_variables: Union[None, Unset, list[str]] = UNSET
    examples: Union[None, Unset, list["PromptCreateExamplesType0Item"]] = UNSET
    test_cases: Union[None, Unset, list["PromptCreateTestCasesType0Item"]] = UNSET
    suggested_temperature: Union[None, Unset, float] = UNSET
    suggested_max_tokens: Union[None, Unset, int] = UNSET
    suggested_providers: Union[None, Unset, list[str]] = UNSET
    is_chain: Union[Unset, bool] = False
    chain_steps: Union[None, Unset, list["PromptCreateChainStepsType0Item"]] = UNSET
    parent_prompt_id: Union[None, Unset, str] = UNSET
    is_public: Union[Unset, bool] = False
    tags: Union[None, Unset, list[str]] = UNSET
    extra_metadata: Union["PromptCreateExtraMetadataType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prompt_create_extra_metadata_type_0 import PromptCreateExtraMetadataType0
        from ..models.prompt_create_input_schema_type_0 import PromptCreateInputSchemaType0
        from ..models.prompt_create_output_schema_type_0 import PromptCreateOutputSchemaType0

        name = self.name

        content = self.content

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        prompt_type: Union[Unset, str] = UNSET
        if not isinstance(self.prompt_type, Unset):
            prompt_type = self.prompt_type.value

        category: Union[Unset, str] = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        variables: Union[None, Unset, list[str]]
        if isinstance(self.variables, Unset):
            variables = UNSET
        elif isinstance(self.variables, list):
            variables = self.variables

        else:
            variables = self.variables

        template_format = self.template_format

        input_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.input_schema, Unset):
            input_schema = UNSET
        elif isinstance(self.input_schema, PromptCreateInputSchemaType0):
            input_schema = self.input_schema.to_dict()
        else:
            input_schema = self.input_schema

        output_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.output_schema, Unset):
            output_schema = UNSET
        elif isinstance(self.output_schema, PromptCreateOutputSchemaType0):
            output_schema = self.output_schema.to_dict()
        else:
            output_schema = self.output_schema

        max_length: Union[None, Unset, int]
        if isinstance(self.max_length, Unset):
            max_length = UNSET
        else:
            max_length = self.max_length

        min_length: Union[None, Unset, int]
        if isinstance(self.min_length, Unset):
            min_length = UNSET
        else:
            min_length = self.min_length

        required_variables: Union[None, Unset, list[str]]
        if isinstance(self.required_variables, Unset):
            required_variables = UNSET
        elif isinstance(self.required_variables, list):
            required_variables = self.required_variables

        else:
            required_variables = self.required_variables

        examples: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.examples, Unset):
            examples = UNSET
        elif isinstance(self.examples, list):
            examples = []
            for examples_type_0_item_data in self.examples:
                examples_type_0_item = examples_type_0_item_data.to_dict()
                examples.append(examples_type_0_item)

        else:
            examples = self.examples

        test_cases: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.test_cases, Unset):
            test_cases = UNSET
        elif isinstance(self.test_cases, list):
            test_cases = []
            for test_cases_type_0_item_data in self.test_cases:
                test_cases_type_0_item = test_cases_type_0_item_data.to_dict()
                test_cases.append(test_cases_type_0_item)

        else:
            test_cases = self.test_cases

        suggested_temperature: Union[None, Unset, float]
        if isinstance(self.suggested_temperature, Unset):
            suggested_temperature = UNSET
        else:
            suggested_temperature = self.suggested_temperature

        suggested_max_tokens: Union[None, Unset, int]
        if isinstance(self.suggested_max_tokens, Unset):
            suggested_max_tokens = UNSET
        else:
            suggested_max_tokens = self.suggested_max_tokens

        suggested_providers: Union[None, Unset, list[str]]
        if isinstance(self.suggested_providers, Unset):
            suggested_providers = UNSET
        elif isinstance(self.suggested_providers, list):
            suggested_providers = self.suggested_providers

        else:
            suggested_providers = self.suggested_providers

        is_chain = self.is_chain

        chain_steps: Union[None, Unset, list[dict[str, Any]]]
        if isinstance(self.chain_steps, Unset):
            chain_steps = UNSET
        elif isinstance(self.chain_steps, list):
            chain_steps = []
            for chain_steps_type_0_item_data in self.chain_steps:
                chain_steps_type_0_item = chain_steps_type_0_item_data.to_dict()
                chain_steps.append(chain_steps_type_0_item)

        else:
            chain_steps = self.chain_steps

        parent_prompt_id: Union[None, Unset, str]
        if isinstance(self.parent_prompt_id, Unset):
            parent_prompt_id = UNSET
        else:
            parent_prompt_id = self.parent_prompt_id

        is_public = self.is_public

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        extra_metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.extra_metadata, Unset):
            extra_metadata = UNSET
        elif isinstance(self.extra_metadata, PromptCreateExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "content": content,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if prompt_type is not UNSET:
            field_dict["prompt_type"] = prompt_type
        if category is not UNSET:
            field_dict["category"] = category
        if variables is not UNSET:
            field_dict["variables"] = variables
        if template_format is not UNSET:
            field_dict["template_format"] = template_format
        if input_schema is not UNSET:
            field_dict["input_schema"] = input_schema
        if output_schema is not UNSET:
            field_dict["output_schema"] = output_schema
        if max_length is not UNSET:
            field_dict["max_length"] = max_length
        if min_length is not UNSET:
            field_dict["min_length"] = min_length
        if required_variables is not UNSET:
            field_dict["required_variables"] = required_variables
        if examples is not UNSET:
            field_dict["examples"] = examples
        if test_cases is not UNSET:
            field_dict["test_cases"] = test_cases
        if suggested_temperature is not UNSET:
            field_dict["suggested_temperature"] = suggested_temperature
        if suggested_max_tokens is not UNSET:
            field_dict["suggested_max_tokens"] = suggested_max_tokens
        if suggested_providers is not UNSET:
            field_dict["suggested_providers"] = suggested_providers
        if is_chain is not UNSET:
            field_dict["is_chain"] = is_chain
        if chain_steps is not UNSET:
            field_dict["chain_steps"] = chain_steps
        if parent_prompt_id is not UNSET:
            field_dict["parent_prompt_id"] = parent_prompt_id
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if tags is not UNSET:
            field_dict["tags"] = tags
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_create_chain_steps_type_0_item import PromptCreateChainStepsType0Item
        from ..models.prompt_create_examples_type_0_item import PromptCreateExamplesType0Item
        from ..models.prompt_create_extra_metadata_type_0 import PromptCreateExtraMetadataType0
        from ..models.prompt_create_input_schema_type_0 import PromptCreateInputSchemaType0
        from ..models.prompt_create_output_schema_type_0 import PromptCreateOutputSchemaType0
        from ..models.prompt_create_test_cases_type_0_item import PromptCreateTestCasesType0Item

        d = dict(src_dict)
        name = d.pop("name")

        content = d.pop("content")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        _prompt_type = d.pop("prompt_type", UNSET)
        prompt_type: Union[Unset, PromptType]
        if isinstance(_prompt_type, Unset):
            prompt_type = UNSET
        else:
            prompt_type = PromptType(_prompt_type)

        _category = d.pop("category", UNSET)
        category: Union[Unset, PromptCategory]
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = PromptCategory(_category)

        def _parse_variables(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                variables_type_0 = cast(list[str], data)

                return variables_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        variables = _parse_variables(d.pop("variables", UNSET))

        template_format = d.pop("template_format", UNSET)

        def _parse_input_schema(data: object) -> Union["PromptCreateInputSchemaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_schema_type_0 = PromptCreateInputSchemaType0.from_dict(data)

                return input_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptCreateInputSchemaType0", None, Unset], data)

        input_schema = _parse_input_schema(d.pop("input_schema", UNSET))

        def _parse_output_schema(data: object) -> Union["PromptCreateOutputSchemaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                output_schema_type_0 = PromptCreateOutputSchemaType0.from_dict(data)

                return output_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptCreateOutputSchemaType0", None, Unset], data)

        output_schema = _parse_output_schema(d.pop("output_schema", UNSET))

        def _parse_max_length(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_length = _parse_max_length(d.pop("max_length", UNSET))

        def _parse_min_length(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        min_length = _parse_min_length(d.pop("min_length", UNSET))

        def _parse_required_variables(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                required_variables_type_0 = cast(list[str], data)

                return required_variables_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        required_variables = _parse_required_variables(d.pop("required_variables", UNSET))

        def _parse_examples(data: object) -> Union[None, Unset, list["PromptCreateExamplesType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                examples_type_0 = []
                _examples_type_0 = data
                for examples_type_0_item_data in _examples_type_0:
                    examples_type_0_item = PromptCreateExamplesType0Item.from_dict(examples_type_0_item_data)

                    examples_type_0.append(examples_type_0_item)

                return examples_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["PromptCreateExamplesType0Item"]], data)

        examples = _parse_examples(d.pop("examples", UNSET))

        def _parse_test_cases(data: object) -> Union[None, Unset, list["PromptCreateTestCasesType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                test_cases_type_0 = []
                _test_cases_type_0 = data
                for test_cases_type_0_item_data in _test_cases_type_0:
                    test_cases_type_0_item = PromptCreateTestCasesType0Item.from_dict(test_cases_type_0_item_data)

                    test_cases_type_0.append(test_cases_type_0_item)

                return test_cases_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["PromptCreateTestCasesType0Item"]], data)

        test_cases = _parse_test_cases(d.pop("test_cases", UNSET))

        def _parse_suggested_temperature(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        suggested_temperature = _parse_suggested_temperature(d.pop("suggested_temperature", UNSET))

        def _parse_suggested_max_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        suggested_max_tokens = _parse_suggested_max_tokens(d.pop("suggested_max_tokens", UNSET))

        def _parse_suggested_providers(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                suggested_providers_type_0 = cast(list[str], data)

                return suggested_providers_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        suggested_providers = _parse_suggested_providers(d.pop("suggested_providers", UNSET))

        is_chain = d.pop("is_chain", UNSET)

        def _parse_chain_steps(data: object) -> Union[None, Unset, list["PromptCreateChainStepsType0Item"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                chain_steps_type_0 = []
                _chain_steps_type_0 = data
                for chain_steps_type_0_item_data in _chain_steps_type_0:
                    chain_steps_type_0_item = PromptCreateChainStepsType0Item.from_dict(chain_steps_type_0_item_data)

                    chain_steps_type_0.append(chain_steps_type_0_item)

                return chain_steps_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["PromptCreateChainStepsType0Item"]], data)

        chain_steps = _parse_chain_steps(d.pop("chain_steps", UNSET))

        def _parse_parent_prompt_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_prompt_id = _parse_parent_prompt_id(d.pop("parent_prompt_id", UNSET))

        is_public = d.pop("is_public", UNSET)

        def _parse_tags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        tags = _parse_tags(d.pop("tags", UNSET))

        def _parse_extra_metadata(data: object) -> Union["PromptCreateExtraMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = PromptCreateExtraMetadataType0.from_dict(data)

                return extra_metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptCreateExtraMetadataType0", None, Unset], data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))

        prompt_create = cls(
            name=name,
            content=content,
            description=description,
            prompt_type=prompt_type,
            category=category,
            variables=variables,
            template_format=template_format,
            input_schema=input_schema,
            output_schema=output_schema,
            max_length=max_length,
            min_length=min_length,
            required_variables=required_variables,
            examples=examples,
            test_cases=test_cases,
            suggested_temperature=suggested_temperature,
            suggested_max_tokens=suggested_max_tokens,
            suggested_providers=suggested_providers,
            is_chain=is_chain,
            chain_steps=chain_steps,
            parent_prompt_id=parent_prompt_id,
            is_public=is_public,
            tags=tags,
            extra_metadata=extra_metadata,
        )

        prompt_create.additional_properties = d
        return prompt_create

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
