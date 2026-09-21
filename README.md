# Palyt Kitchen

A small tool that connects a kitchen's stock to the restaurant's menu, so a
dish is automatically marked unavailable when it runs short of an ingredient.

## Running it

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000 in a browser.

## Running the tests

```bash
pytest
```

(Test coverage for stock and menu logic will grow as those pieces are built.)

## Status

Work in progress - see commit history for progress. This section and the
write-up will be filled in as the project is completed.
