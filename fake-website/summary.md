# EmpathAI Calibration Site: Accessibility Violation Summary

This document summarizes the 20 intentional WCAG 2.1 AA violations embedded in `index.html`.

## 🔴 Critical Severity (Blocks Access)
1.  **Missing Lang Attribute (3.1.1):** Screen readers cannot determine the correct voice profile.
2.  **Missing Alt Text (1.1.1):** Logo image is invisible to screen readers.
3.  **Missing Form Label (1.3.1):** The "Username" input has no programmatic label, only a placeholder.
4.  **Non-Semantic Button (4.1.2):** A `div` is used as a button; it is unreachable via keyboard and lacks a role.
5.  **Keyboard Trap (2.1.1):** The "Widgets" section contains an input that prevents the user from tabbing out.
6.  **Broken Modal (2.1.1):** The modal does not trap focus, allowing the user to tab incorrectly into the background page.
7.  **Missing Captions (1.2.2):** The video element has no closed captions.

## 🟠 Serious Severity (Major Hindrance)
8.  **Low Contrast (1.4.3):** The paragraph text (`.low-contrast`) falls below the 4.5:1 ratio.
9.  **Vague Link Text (2.4.4):** "Click here" provides no context out of sequence.
10. **Invalid ARIA (4.1.2):** `aria-describedby` points to a non-existent ID on the email input.
11. **Positive Tabindex (2.4.3):** A button explicitly sets `tabindex="1"`, breaking natural navigation flow.
12. **Missing Skip Link (2.4.1):** Users cannot bypass the navigation menu.
13. **Missing Status Message (4.1.3):** The stock ticker updates visually but is silent for screen readers (missing `aria-live`).
14. **Visual Order Mismatch (2.4.3):** Navigation uses CSS `row-reverse`, making keyboard navigation go backwards visually.
15. **Use of Color Alone (1.4.1):** Red borders indicate required fields with no text alternative.

## 🟡 Moderate/Minor Severity
16. **Decorative Image Alt (1.1.1):** A decorative swoosh has alt text, creating noise for AT users.
17. **Heading Order (2.4.6):** An `<h3>` appears before an `<h2>`.
18. **New Window Link (2.4.2):** Link opens a new tab without `rel="noopener"` or a text warning.
19. **Image of Text (1.4.5):** The hero image uses pixels for text rather than CSS.
20. **Live Region Misuse (4.1.2):** An element has `role="status"` but acts as a focusable tab stop.

---
**Total Issues:** 20
**Standard:** WCAG 2.1 AA