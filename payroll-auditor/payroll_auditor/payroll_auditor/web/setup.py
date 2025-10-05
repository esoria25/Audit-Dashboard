from setuptools import setup, find_packages

setup(
    name="payroll-auditor-tool",
    version="1.0.0",
    author="Payroll Auditor Team",
    description="A comprehensive tool for comparing and auditing payroll data",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "openpyxl>=3.0.7",
        "PyPDF2>=2.10.0",
        "pdfplumber>=0.6.0",
        "Flask>=2.0.0",
        "reportlab>=3.6.0",
        "python-Levenshtein>=0.12.2",
        "fuzzywuzzy>=0.18.0",
        "PyYAML>=5.4.0",
        "click>=8.0.0",
        "colorama>=0.4.4",
    ],
    entry_points={
        "console_scripts": [
            "payroll-auditor=payroll_auditor.cli.main:main",
        ],
    },
)
