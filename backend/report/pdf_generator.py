# backend/report/pdf_generator.py
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from datetime import datetime
import base64

# Setup Jinja2
template_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(loader=FileSystemLoader(template_dir))

def generate_pdf_report(report_data: dict, url: str) -> bytes:
    """
    Generates a beautiful branded PDF report
    Returns bytes (for download)
    """
    template = env.get_template("report.html")

    # Add metadata
    report_data.update({
        "url": url,
        "generated_at": datetime.now().strftime("%d %B %Y, %I:%M %p"),
        "total_issues": len(report_data.get("report", [])),
        "india_compliant": report_data["summary"]["india_compliance"] == "PASS",
        "empathai_version": "v2.0"
    })

    html_content = template.render(report_data)

    # Convert to PDF
    pdf_bytes = HTML(string=html_content, base_url=os.path.dirname(__file__)).write_pdf()

    return pdf_bytes