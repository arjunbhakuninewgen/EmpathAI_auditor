import os
import json

# Placeholder for Bhashini API Key
BHASHINI_API_KEY = os.getenv("BHASHINI_API_KEY", "mock-key")

def translate_text(text: str, target_lang: str = "hi") -> str:
    """
    Translates text into the target Indic language using Bhashini API.
    
    Args:
        text (str): The text to translate (usually English).
        target_lang (str): ISO code for target language (e.g., 'hi' for Hindi, 'ta' for Tamil).
        
    Returns:
        str: The translated text.
    """
    print(f"🇮🇳 BHASHINI: Translating to {target_lang}...")
    
    # --- MOCK IMPLEMENTATION FOR DEMO ---
    # In a real scenario, this would make a POST request to Bhashini NMT API
    
    if not text:
        return ""

    # Simple mock translations for common phrases to make the demo look real
    mock_translations = {
        "hi": {
            "Fix this WCAG Violation.": "इस WCAG उल्लंघन को ठीक करें।",
            "Focus indicator disappeared.": "फोकस संकेतक गायब हो गया।",
            "Manual review recommended.": "मैनुअल समीक्षा की सिफारिश की गई है।",
            "Check CSS contrast/spacing.": "CSS कंट्रास्ट/स्पेसिंग की जाँच करें।",
            "Update the text or structure.": "पाठ या संरचना को अपडेट करें।"
        },
        "ta": {
            "Fix this WCAG Violation.": "இந்த WCAG மீறலை சரிசெய்யவும்.",
            "Focus indicator disappeared.": "கவனக் குறி மறைந்துவிட்டது."
        }
    }
    
    # Return mock if exists, else return a pseudo-translation
    if target_lang in mock_translations and text in mock_translations[target_lang]:
        return mock_translations[target_lang][text]
    
    # Fallback for dynamic text: just append language tag
    return f"[{target_lang.upper()}] {text}"

# Example usage for testing
if __name__ == "__main__":
    print(translate_text("Fix this WCAG Violation.", "hi"))
