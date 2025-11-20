# EmpathAI Testbed Site

This is a lightweight, intentionally broken single-page website designed to test the capabilities of **EmpathAI** (Accessibility Auditing Agent).

It contains exactly **20 unique WCAG 2.1 AA violations**, covering visual rendering, semantic structure, keyboard navigation, and ARIA usage.

## 🚀 How to Run

This site requires no build process or server.

1.  **Download** the files (`index.html`, `styles.css`, `script.js`).
2.  **Open** `index.html` directly in your browser (double click or drag-and-drop).
3.  **Scan** the URL (file path) using your EmpathAI scanner.

## 🧪 Testing the Scanner

Your scanner should detect the issues listed in `report.json`.

### Key Testing Areas:
1.  **Dynamic Content:** Wait 3 seconds after load. A new div appears. The scanner should handle this or miss it depending on its wait logic.
2.  **Keyboard Traps:** The "Widgets" section traps focus. The scanner (Playwright) should detect this or time out.
3.  **Contrast:** Text in `.low-contrast` is #999 on White (2.84:1).
4.  **True Negative:** The button with class `.good-contrast` should **not** trigger a violation.

## 📂 Deliverables
- **Source Code:** `index.html`, `styles.css`, `script.js`
- **Ground Truth:** `report.json`
- **Explanation:** `summary.md`