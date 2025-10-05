"""
Payroll Auditor Tool
A comprehensive tool for comparing and auditing payroll data across different file formats.
"""

__version__ = "1.0.0"
__author__ = "Payroll Auditor Team"

try:
    from .core.auditor import PayrollAuditor
    from .core.models import AuditResult, EmployeeRecord, Discrepancy
    __all__ = ["PayrollAuditor", "AuditResult", "EmployeeRecord", "Discrepancy"]
except ImportError:
    # Handle case where dependencies aren't installed yet
    __all__ = []
