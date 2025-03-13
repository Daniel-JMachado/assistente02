# CLAUDE.md - Dev Guidelines

## Environment Setup
- Create virtual environment: `python -m venv venv`
- Activate: Windows `venv\Scripts\activate`, Unix `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Set ANTHROPIC_API_KEY in .env file

## Run Commands
- Launch app: `streamlit run app.py`
- Run specific test: `pytest tests/test_filename.py::test_function_name -v`
- Lint code: `flake8 . --max-line-length=100`
- Type check: `mypy --ignore-missing-imports .`

## Code Style Guidelines
- **Imports**: Standard libs first, then third-party, then local
- **Naming**: Snake_case for variables/functions, PascalCase for classes
- **Documentation**: Functions need docstrings with Args/Returns sections
- **Error Handling**: Use try/except with specific exceptions and meaningful messages
- **Type Hints**: Use for all function parameters and return values
- **Max Line Length**: 100 characters
- **String Formatting**: Use f-strings over other formats

## Project Structure
- Main UI in app.py
- Core logic in chat.py
- PDF documents in documentos/