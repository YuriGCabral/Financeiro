# Assets Folder

This folder contains static assets for the Streamlit application.

## Contents

- `lucide_data.json` - SVG icon data for Lucide icons used in the UI

## Important Notes

### Linux Compatibility
- All paths use lowercase to ensure compatibility with Linux systems (Streamlit Cloud)
- No relative paths (`../`) are used - all references are from the repo root
- Files are committed to git (whitelisted in `.gitignore`)

### Usage in Code

The icons are loaded by `organizador/lucide.py` using:

```python
_DATA_PATH = Path(__file__).parent.parent / "assets" / "lucide_data.json"
```

### Validation

To verify assets are properly loaded, the code includes a validation function:

```python
from organizador.lucide import validate_assets

if validate_assets():
    print("Assets loaded successfully!")
```

## Adding New Assets

When adding new images or assets:

1. Place files in this `/assets` folder (repo root)
2. Use lowercase filenames (e.g., `logo.png`, not `Logo.PNG`)
3. Reference with `"assets/filename.png"` (no relative paths)
4. Update `.gitignore` if needed (add exceptions like `!assets/*.png`)
5. Commit to git: `git add assets/` and `git commit`
