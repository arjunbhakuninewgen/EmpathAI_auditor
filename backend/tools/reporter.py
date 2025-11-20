from datetime import datetime

def generate_report(url, mapped_issues):
    """
    Organizes the data into a structured JSON report.
    """
    
    # 1. Count the stats
    critical_count = sum(1 for i in mapped_issues if i['impact'] == 'critical')
    serious_count = sum(1 for i in mapped_issues if i['impact'] == 'serious')
    
    # 2. Build the report structure
    report = {
        "metadata": {
            "url": url,
            "scan_date": datetime.now().isoformat(),
            "total_issues": len(mapped_issues),
            "severity_breakdown": {
                "critical": critical_count,
                "serious": serious_count,
                "minor": len(mapped_issues) - critical_count - serious_count
            }
        },
        "compliance_status": "Failed" if len(mapped_issues) > 0 else "Passed",
        "issues": mapped_issues
    }
    
    return report