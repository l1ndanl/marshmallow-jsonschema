from marshmallow import fields

from .exceptions import UnsupportedValueError


def handle_length(schema, field, validator, parent_schema):
    """Adds validation logic for ``marshmallow.validate.Length``, setting the
    values appropriately for ``fields.List``, ``fields.Nested``, and
    ``fields.String``.

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.Length): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: A, possibly, new JSON Schema that has been post processed and
            altered.

    Raises:
        UnsupportedValueError: Raised if the `field` is something other than
            `fields.List`, `fields.Nested`, or `fields.String`
    """
    if isinstance(field, fields.String):
        minKey = "minLength"
        maxKey = "maxLength"
    elif isinstance(field, (fields.List, fields.Nested)):
        minKey = "minItems"
        maxKey = "maxItems"
    else:
        raise UnsupportedValueError(
            "In order to set the Length validator for JSON "
            "schema, the field must be either a List, Nested or a String"
        )

    if validator.min:
        schema[minKey] = validator.min

    if validator.max:
        schema[maxKey] = validator.max

    if validator.equal:
        schema[minKey] = validator.equal
        schema[maxKey] = validator.equal

    return schema


def handle_one_of(schema, field, validator, parent_schema):
    """Adds the validation logic for ``marshmallow.validate.OneOf`` by setting
    the JSONSchema `enum` property to the allowed choices in the validator.

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.OneOf): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: New JSON Schema that has been post processed and
            altered.
    """
    schema["enum"] = list(validator.choices)
    schema["enumNames"] = list(validator.labels)

    return schema


def handle_range(schema, field, validator, parent_schema):
    """Adds validation logic for ``marshmallow.validate.Range``, setting the
    values appropriately ``fields.Number`` and it's subclasses.

    Args:
        schema (dict): The original JSON schema we generated. This is what we
            want to post-process.
        field (fields.Field): The field that generated the original schema and
            who this post-processor belongs to.
        validator (marshmallow.validate.Range): The validator attached to the
            passed in field.
        parent_schema (marshmallow.Schema): The Schema instance that the field
            belongs to.

    Returns:
        dict: New JSON Schema that has been post processed and
            altered.

    Raises:
        UnsupportedValueError: Raised if the `field` is not an instance of
            `fields.Number`.
    """
    if not isinstance(field, fields.Number):
        raise UnsupportedValueError(
            "'Range' validator for non-number fields is not supported"
        )

    if validator.min is not None:
        # marshmallow 2 includes minimum by default
        # marshmallow 3 supports "min_inclusive"
        min_inclusive = getattr(validator, "min_inclusive", True)
        if min_inclusive:
            schema["minimum"] = validator.min
        else:
            schema["exclusiveMinimum"] = validator.min

    if validator.max is not None:
        # marshmallow 2 includes maximum by default
        # marshmallow 3 supports "max_inclusive"
        max_inclusive = getattr(validator, "max_inclusive", True)
        if max_inclusive:
            schema["maximum"] = validator.max
        else:
            schema["exclusiveMaximum"] = validator.max
    return schema
