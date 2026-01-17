from dataclasses import dataclass


@dataclass
class LLMCallInput:
    prompt: str


@dataclass
class PDFGenerationInput:
    content: str
    filename: str = "research_output.pdf"


@dataclass
class GenerateReportInput:
    prompt: str
