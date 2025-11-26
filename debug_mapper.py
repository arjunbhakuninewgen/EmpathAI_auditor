try:
    from backend.tools import wcag_mapper
    print("Import successful")
except SyntaxError as e:
    print(f"SyntaxError: {e}")
    print(f"Line: {e.lineno}")
    print(f"Offset: {e.offset}")
    print(f"Text: {e.text}")
except Exception as e:
    print(f"Error: {e}")
