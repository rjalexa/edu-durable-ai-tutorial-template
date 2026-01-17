from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
import re

with workflow.unsafe.imports_passed_through():
    from temporal.activities import create_pdf, llm_call
    from temporal.models import (
        GenerateReportInput,
        LLMCallInput,
        PDFGenerationInput,
    )


def create_filename_abstract(prompt: str, workflow_id: str, max_words: int = 5) -> str:
    """
    Create a sanitized filename combining an abstract of the prompt with the workflow ID.
    
    Args:
        prompt: The original question/prompt text
        workflow_id: The workflow execution ID
        max_words: Maximum number of words to include from the prompt
    
    Returns:
        A filesystem-safe filename string
    """
    # Extract first N words from the prompt
    words = prompt.split()[:max_words]
    abstract = " ".join(words)
    
    # Remove special characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', abstract)
    sanitized = re.sub(r'[\s]+', '_', sanitized)
    
    # Truncate if too long and combine with workflow ID
    max_abstract_length = 50
    if len(sanitized) > max_abstract_length:
        sanitized = sanitized[:max_abstract_length].rstrip('_')
    
    # Create final filename
    filename = f"{sanitized}_{workflow_id}.pdf"
    
    return filename


@workflow.defn
class GenerateReportWorkflow:
    @workflow.run
    async def run(self, input: GenerateReportInput) -> str:
        # Get the workflow ID for the filename
        workflow_id = workflow.info().workflow_id
        
        # Create dynamic filename combining prompt abstract and workflow ID
        pdf_filename = create_filename_abstract(input.prompt, workflow_id)
        
        llm_call_input = LLMCallInput(prompt=input.prompt)

        # Step 1: Call LLM Activity to generate research
        research_facts = await workflow.execute_activity(
            llm_call,
            llm_call_input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        pdf_generation_input = PDFGenerationInput(
            content=research_facts["choices"][0]["message"]["content"],
            filename=pdf_filename
        )

        # Step 2: Create PDF Activity
        pdf_filename = await workflow.execute_activity(
            create_pdf,
            pdf_generation_input,
            start_to_close_timeout=timedelta(seconds=20),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_attempts=3,
                backoff_coefficient=3.0,
            ),
        )

        return f"Successfully created research report PDF: {pdf_filename}"
