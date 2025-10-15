## Style Guide
Follow `Google Python Style Guide`.

Indent code blocks with 2 spaces. Never use tabs. Implied line continuation should align wrapped elements vertically, or use a hanging 4-space indent. Closing brackets can be placed at the end of the expression, or on separate lines, but then should be indented the same as the line with the corresponding opening bracket.

Always run `pylint` and fix the issues after wrapping a code change.

## Building and running
The project is managed by using `uv`. Use `uv` to execute any Python-related commands.

## Formatting
Always run `pyink` to fix code format.

## Testing
Use Python built-in `unittest` module to write test cases. And run unit tests using `pytest`.