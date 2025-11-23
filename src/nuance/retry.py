"""
Retry mechanism for LLM output validation.

This module implements a self-correction loop: when Pydantic validation fails,
we feed the error message back to Claude and ask it to fix the JSON.

This is the "Guardrails" pattern that significantly reduces parsing errors.
"""

import json
from typing import TypeVar, Type, Callable, Any
from pydantic import BaseModel, ValidationError
import anthropic

T = TypeVar('T', bound=BaseModel)


class RetryExhaustedError(Exception):
    """Raised when max retries are exceeded without successful validation."""
    pass


def validate_with_retry(
    client: anthropic.Anthropic,
    model: str,
    initial_messages: list,
    schema_class: Type[T],
    max_retries: int = 3,
    temperature: float = 0.0
) -> T:
    """
    Call Claude with automatic retry on validation failures.

    This function:
    1. Calls Claude with the initial prompt
    2. Attempts to parse the response into the Pydantic schema
    3. If validation fails, sends the error back to Claude asking it to fix
    4. Retries up to max_retries times

    Args:
        client: Anthropic API client
        model: Model name (e.g., "claude-sonnet-4-5-20250929")
        initial_messages: List of message dicts for the API call
        schema_class: Pydantic model class to validate against
        max_retries: Maximum number of retry attempts
        temperature: Temperature for Claude (0.0 = deterministic)

    Returns:
        Validated instance of schema_class

    Raises:
        RetryExhaustedError: If validation fails after max_retries attempts
    """
    messages = initial_messages.copy()
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            # Call Claude
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=temperature,
                messages=messages
            )

            # Extract text content
            response_text = response.content[0].text

            # Try to parse JSON from response
            # Handle cases where Claude wraps JSON in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()

            # Parse JSON
            data = json.loads(json_str)

            # Validate with Pydantic
            validated_data = schema_class.model_validate(data)

            # Success!
            return validated_data

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            error_type = "JSON parsing" if isinstance(e, json.JSONDecodeError) else "Schema validation"

            if attempt < max_retries:
                # Prepare retry message with error feedback
                error_message = f"""
{error_type} error occurred. Please fix the JSON and try again.

Error details:
{str(e)}

Requirements:
1. Your response must be valid JSON
2. It must match this schema exactly: {schema_class.__name__}
3. Check all required fields are present
4. Ensure all field types are correct (strings, numbers, booleans, etc.)
5. Validate that numeric fields are in the correct ranges

Please output ONLY the corrected JSON, with no additional text or explanation.
"""
                # Add the assistant's failed response and our error feedback
                messages.extend([
                    {"role": "assistant", "content": response_text if 'response_text' in locals() else ""},
                    {"role": "user", "content": error_message}
                ])

            else:
                # Max retries exceeded
                raise RetryExhaustedError(
                    f"Failed to get valid {schema_class.__name__} after {max_retries + 1} attempts. "
                    f"Last error: {str(last_error)}"
                )

    # Should never reach here, but just in case
    raise RetryExhaustedError(f"Unexpected error in retry loop. Last error: {str(last_error)}")


def extract_json_from_text(text: str) -> str:
    """
    Helper function to extract JSON from Claude's response.
    Handles cases where JSON is wrapped in markdown code blocks.
    """
    text = text.strip()

    # Case 1: Wrapped in ```json ... ```
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        return text[start:end].strip()

    # Case 2: Wrapped in ``` ... ``` (generic code block)
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        return text[start:end].strip()

    # Case 3: Raw JSON
    else:
        return text
