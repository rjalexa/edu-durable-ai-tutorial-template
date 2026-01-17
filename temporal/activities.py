import os
from typing import cast
from dotenv import load_dotenv
from litellm import completion
from litellm.types.utils import ModelResponse
from temporal.models import LLMCallInput, PDFGenerationInput
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable
from temporalio import activity

load_dotenv(override=True)  # Reads your .env file and loads your environment variables

# Get LLM_API_KEY environment variable
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-4o")
LLM_API_KEY = os.getenv("LLM_API_KEY", None)


@activity.defn
def llm_call(input: LLMCallInput) -> ModelResponse:
    return cast(
        ModelResponse,
        completion(
            model=LLM_MODEL,
            api_key=LLM_API_KEY,
            messages=[{"content": input.prompt, "role": "user"}],
            stream=False,
        ),
    )


@activity.defn
def create_pdf(input: PDFGenerationInput) -> str:
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create the full path for the PDF file
    filepath = os.path.join(reports_dir, input.filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
    )

    story: list[Flowable] = []
    title = Paragraph("Research Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))

    paragraphs = input.content.split("\n\n")
    for para in paragraphs:
        if para.strip():
            p = Paragraph(para.strip(), styles["Normal"])
            story.append(p)
            story.append(Spacer(1, 12))

    doc.build(story)
    return filepath
