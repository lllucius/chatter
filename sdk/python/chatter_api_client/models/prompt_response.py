import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.prompt_category import PromptCategory
from ..models.prompt_type import PromptType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prompt_response_chain_steps_type_0_item import PromptResponseChainStepsType0Item
    from ..models.prompt_response_examples_type_0_item import PromptResponseExamplesType0Item
    from ..models.prompt_response_extra_metadata_type_0 import PromptResponseExtraMetadataType0
    from ..models.prompt_response_input_schema_type_0 import PromptResponseInputSchemaType0
    from ..models.prompt_response_output_schema_type_0 import PromptResponseOutputSchemaType0
    from ..models.prompt_response_test_cases_type_0_item import PromptResponseTestCasesType0Item


T = TypeVar("T", bound="PromptResponse")


@_attrs_define
class PromptResponse:
    """Schema for prompt response.

    Attributes:
        id (str): Prompt ID
        owner_id (str): Owner user ID
        name (str): Prompt name
        prompt_type (PromptType): Enumeration for prompt types.
        category (PromptCategory): Enumeration for prompt categories.
        content (str): Prompt content/template
        template_format (str): Template format
        is_chain (bool): Whether this is a chain prompt
        version (int): Prompt version
        is_latest (bool): Whether this is the latest version
        is_public (bool): Whether prompt is public
        rating_count (int): Number of ratings
        usage_count (int): Usage count
        total_tokens_used (int): Total tokens used
        total_cost (float): Total cost
        content_hash (str): Content hash
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        description (Union[None, Unset, str]): Prompt description
        variables (Union[None, Unset, list[str]]): Template variables
        input_schema (Union['PromptResponseInputSchemaType0', None, Unset]): Input validation schema
        output_schema (Union['PromptResponseOutputSchemaType0', None, Unset]): Output validation schema
        max_length (Union[None, Unset, int]): Maximum content length
        min_length (Union[None, Unset, int]): Minimum content length
        required_variables (Union[None, Unset, list[str]]): Required template variables
        examples (Union[None, Unset, list['PromptResponseExamplesType0Item']]): Usage examples
        test_cases (Union[None, Unset, list['PromptResponseTestCasesType0Item']]): Test cases
        suggested_temperature (Union[None, Unset, float]): Suggested temperature
        suggested_max_tokens (Union[None, Unset, int]): Suggested max tokens
        suggested_providers (Union[None, Unset, list[str]]): Suggested LLM providers
        chain_steps (Union[None, Unset, list['PromptResponseChainStepsType0Item']]): Chain execution steps
        parent_prompt_id (Union[None, Unset, str]): Parent prompt ID
        changelog (Union[None, Unset, str]): Version changelog
        rating (Union[None, Unset, float]): Average rating
        success_rate (Union[None, Unset, float]): Success rate
        avg_response_time_ms (Union[None, Unset, int]): Average response time
        last_used_at (Union[None, Unset, datetime.datetime]): Last used timestamp
        avg_tokens_per_use (Union[None, Unset, float]): Average tokens per use
        tags (Union[None, Unset, list[str]]): Prompt tags
        extra_metadata (Union['PromptResponseExtraMetadataType0', None, Unset]): Additional metadata
        estimated_tokens (Union[None, Unset, int]): Estimated token count
        language (Union[None, Unset, str]): Content language
    """

    id: str
    owner_id: str
    name: str
    prompt_type: PromptType
    category: PromptCategory
    content: str
    template_format: str
    is_chain: bool
    version: int
    is_latest: bool
    is_public: bool
    rating_count: int
    usage_count: int
    total_tokens_used: int
    total_cost: float
    content_hash: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    variables: Union[None, Unset, list[str]] = UNSET
    input_schema: Union["PromptResponseInputSchemaType0", None, Unset] = UNSET
    output_schema: Union["PromptResponseOutputSchemaType0", None, Unset] = UNSET
    max_length: Union[None, Unset, int] = UNSET
    min_length: Union[None, Unset, int] = UNSET
    required_variables: Union[None, Unset, list[str]] = UNSET
    examples: Union[None, Unset, list["PromptResponseExamplesType0Item"]] = UNSET
    test_cases: Union[None, Unset, list["PromptResponseTestCasesType0Item"]] = UNSET
    suggested_temperature: Union[None, Unset, float] = UNSET
    suggested_max_tokens: Union[None, Unset, int] = UNSET
    suggested_providers: Union[None, Unset, list[str]] = UNSET
    chain_steps: Union[None, Unset, list["PromptResponseChainStepsType0Item"]] = UNSET
    parent_prompt_id: Union[None, Unset, str] = UNSET
    changelog: Union[None, Unset, str] = UNSET
    rating: Union[None, Unset, float] = UNSET
    success_rate: Union[None, Unset, float] = UNSET
    avg_response_time_ms: Union[None, Unset, int] = UNSET
    last_used_at: Union[None, Unset, datetime.datetime] = UNSET
    avg_tokens_per_use: Union[None, Unset, float] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    extra_metadata: Union["PromptResponseExtraMetadataType0", None, Unset] = UNSET
    estimated_tokens: Union[None, Unset, int] = UNSET
    language: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prompt_response_extra_metadata_type_0 import PromptResponseExtraMetadataType0
        from ..models.prompt_response_input_schema_type_0 import PromptResponseInputSchemaType0
        from ..models.prompt_response_output_schema_type_0 import PromptResponseOutputSchemaType0

        id = self.id

        owner_id = self.owner_id

        name = self.name

        prompt_type = self.prompt_type.value

        category = self.category.value

        content = self.content

        template_format = self.template_format

        is_chain = self.is_chain

        version = self.version

        is_latest = self.is_latest

        is_public = self.is_public

        rating_count = self.rating_count

        usage_count = self.usage_count

        total_tokens_used = self.total_tokens_used

        total_cost = self.total_cost

        content_hash = self.content_hash

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        variables: Union[None, Unset, list[str]]
        if isinstance(self.variables, Unset):
            variables = UNSET
        elif isinstance(self.variables, list):
            variables = self.variables

        else:
            variables = self.variables

        input_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.input_schema, Unset):
            input_schema = UNSET
        elif isinstance(self.input_schema, PromptResponseInputSchemaType0):
            input_schema = self.input_schema.to_dict()
        else:
            input_schema = self.input_schema

        output_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.output_schema, Unset):
            output_schema = UNSET
        elif isinstance(self.output_schema, PromptResponseOutputSchemaType0):
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

        changelog: Union[None, Unset, str]
        if isinstance(self.changelog, Unset):
            changelog = UNSET
        else:
            changelog = self.changelog

        rating: Union[None, Unset, float]
        if isinstance(self.rating, Unset):
            rating = UNSET
        else:
            rating = self.rating

        success_rate: Union[None, Unset, float]
        if isinstance(self.success_rate, Unset):
            success_rate = UNSET
        else:
            success_rate = self.success_rate

        avg_response_time_ms: Union[None, Unset, int]
        if isinstance(self.avg_response_time_ms, Unset):
            avg_response_time_ms = UNSET
        else:
            avg_response_time_ms = self.avg_response_time_ms

        last_used_at: Union[None, Unset, str]
        if isinstance(self.last_used_at, Unset):
            last_used_at = UNSET
        elif isinstance(self.last_used_at, datetime.datetime):
            last_used_at = self.last_used_at.isoformat()
        else:
            last_used_at = self.last_used_at

        avg_tokens_per_use: Union[None, Unset, float]
        if isinstance(self.avg_tokens_per_use, Unset):
            avg_tokens_per_use = UNSET
        else:
            avg_tokens_per_use = self.avg_tokens_per_use

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
        elif isinstance(self.extra_metadata, PromptResponseExtraMetadataType0):
            extra_metadata = self.extra_metadata.to_dict()
        else:
            extra_metadata = self.extra_metadata

        estimated_tokens: Union[None, Unset, int]
        if isinstance(self.estimated_tokens, Unset):
            estimated_tokens = UNSET
        else:
            estimated_tokens = self.estimated_tokens

        language: Union[None, Unset, str]
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "owner_id": owner_id,
                "name": name,
                "prompt_type": prompt_type,
                "category": category,
                "content": content,
                "template_format": template_format,
                "is_chain": is_chain,
                "version": version,
                "is_latest": is_latest,
                "is_public": is_public,
                "rating_count": rating_count,
                "usage_count": usage_count,
                "total_tokens_used": total_tokens_used,
                "total_cost": total_cost,
                "content_hash": content_hash,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if variables is not UNSET:
            field_dict["variables"] = variables
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
        if chain_steps is not UNSET:
            field_dict["chain_steps"] = chain_steps
        if parent_prompt_id is not UNSET:
            field_dict["parent_prompt_id"] = parent_prompt_id
        if changelog is not UNSET:
            field_dict["changelog"] = changelog
        if rating is not UNSET:
            field_dict["rating"] = rating
        if success_rate is not UNSET:
            field_dict["success_rate"] = success_rate
        if avg_response_time_ms is not UNSET:
            field_dict["avg_response_time_ms"] = avg_response_time_ms
        if last_used_at is not UNSET:
            field_dict["last_used_at"] = last_used_at
        if avg_tokens_per_use is not UNSET:
            field_dict["avg_tokens_per_use"] = avg_tokens_per_use
        if tags is not UNSET:
            field_dict["tags"] = tags
        if extra_metadata is not UNSET:
            field_dict["extra_metadata"] = extra_metadata
        if estimated_tokens is not UNSET:
            field_dict["estimated_tokens"] = estimated_tokens
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_response_chain_steps_type_0_item import PromptResponseChainStepsType0Item
        from ..models.prompt_response_examples_type_0_item import PromptResponseExamplesType0Item
        from ..models.prompt_response_extra_metadata_type_0 import PromptResponseExtraMetadataType0
        from ..models.prompt_response_input_schema_type_0 import PromptResponseInputSchemaType0
        from ..models.prompt_response_output_schema_type_0 import PromptResponseOutputSchemaType0
        from ..models.prompt_response_test_cases_type_0_item import PromptResponseTestCasesType0Item

        d = dict(src_dict)
        id = d.pop("id")

        owner_id = d.pop("owner_id")

        name = d.pop("name")

        prompt_type = PromptType(d.pop("prompt_type"))

        category = PromptCategory(d.pop("category"))

        content = d.pop("content")

        template_format = d.pop("template_format")

        is_chain = d.pop("is_chain")

        version = d.pop("version")

        is_latest = d.pop("is_latest")

        is_public = d.pop("is_public")

        rating_count = d.pop("rating_count")

        usage_count = d.pop("usage_count")

        total_tokens_used = d.pop("total_tokens_used")

        total_cost = d.pop("total_cost")

        content_hash = d.pop("content_hash")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

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

        def _parse_input_schema(data: object) -> Union["PromptResponseInputSchemaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_schema_type_0 = PromptResponseInputSchemaType0.from_dict(data)

                return input_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptResponseInputSchemaType0", None, Unset], data)

        input_schema = _parse_input_schema(d.pop("input_schema", UNSET))

        def _parse_output_schema(data: object) -> Union["PromptResponseOutputSchemaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                output_schema_type_0 = PromptResponseOutputSchemaType0.from_dict(data)

                return output_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptResponseOutputSchemaType0", None, Unset], data)

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

        def _parse_examples(data: object) -> Union[None, Unset, list["PromptResponseExamplesType0Item"]]:
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
                    examples_type_0_item = PromptResponseExamplesType0Item.from_dict(examples_type_0_item_data)

                    examples_type_0.append(examples_type_0_item)

                return examples_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["PromptResponseExamplesType0Item"]], data)

        examples = _parse_examples(d.pop("examples", UNSET))

        def _parse_test_cases(data: object) -> Union[None, Unset, list["PromptResponseTestCasesType0Item"]]:
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
                    test_cases_type_0_item = PromptResponseTestCasesType0Item.from_dict(test_cases_type_0_item_data)

                    test_cases_type_0.append(test_cases_type_0_item)

                return test_cases_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["PromptResponseTestCasesType0Item"]], data)

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

        def _parse_chain_steps(data: object) -> Union[None, Unset, list["PromptResponseChainStepsType0Item"]]:
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
                    chain_steps_type_0_item = PromptResponseChainStepsType0Item.from_dict(chain_steps_type_0_item_data)

                    chain_steps_type_0.append(chain_steps_type_0_item)

                return chain_steps_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list["PromptResponseChainStepsType0Item"]], data)

        chain_steps = _parse_chain_steps(d.pop("chain_steps", UNSET))

        def _parse_parent_prompt_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        parent_prompt_id = _parse_parent_prompt_id(d.pop("parent_prompt_id", UNSET))

        def _parse_changelog(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        changelog = _parse_changelog(d.pop("changelog", UNSET))

        def _parse_rating(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        rating = _parse_rating(d.pop("rating", UNSET))

        def _parse_success_rate(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        success_rate = _parse_success_rate(d.pop("success_rate", UNSET))

        def _parse_avg_response_time_ms(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        avg_response_time_ms = _parse_avg_response_time_ms(d.pop("avg_response_time_ms", UNSET))

        def _parse_last_used_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_at_type_0 = isoparse(data)

                return last_used_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_used_at = _parse_last_used_at(d.pop("last_used_at", UNSET))

        def _parse_avg_tokens_per_use(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        avg_tokens_per_use = _parse_avg_tokens_per_use(d.pop("avg_tokens_per_use", UNSET))

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

        def _parse_extra_metadata(data: object) -> Union["PromptResponseExtraMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_metadata_type_0 = PromptResponseExtraMetadataType0.from_dict(data)

                return extra_metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptResponseExtraMetadataType0", None, Unset], data)

        extra_metadata = _parse_extra_metadata(d.pop("extra_metadata", UNSET))

        def _parse_estimated_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        estimated_tokens = _parse_estimated_tokens(d.pop("estimated_tokens", UNSET))

        def _parse_language(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        language = _parse_language(d.pop("language", UNSET))

        prompt_response = cls(
            id=id,
            owner_id=owner_id,
            name=name,
            prompt_type=prompt_type,
            category=category,
            content=content,
            template_format=template_format,
            is_chain=is_chain,
            version=version,
            is_latest=is_latest,
            is_public=is_public,
            rating_count=rating_count,
            usage_count=usage_count,
            total_tokens_used=total_tokens_used,
            total_cost=total_cost,
            content_hash=content_hash,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            variables=variables,
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
            chain_steps=chain_steps,
            parent_prompt_id=parent_prompt_id,
            changelog=changelog,
            rating=rating,
            success_rate=success_rate,
            avg_response_time_ms=avg_response_time_ms,
            last_used_at=last_used_at,
            avg_tokens_per_use=avg_tokens_per_use,
            tags=tags,
            extra_metadata=extra_metadata,
            estimated_tokens=estimated_tokens,
            language=language,
        )

        prompt_response.additional_properties = d
        return prompt_response

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
