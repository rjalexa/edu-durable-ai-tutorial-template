import asyncio
import uuid

from models import GenerateReportInput # dataclass for Workflow input
from temporalio.client import Client #  Connects to the Temporal service to start Workflows
from temporalio.contrib.pydantic import pydantic_data_converter
from workflow import GenerateReportWorkflow # Your Workflow definition

async def main():
    # Connect to the Temporal service
    client = await Client.connect(
        "localhost:7233",
        namespace="default",
        data_converter=pydantic_data_converter,
    )

    # Get user input for research topic
    print("Welcome to the Research Report Generator!")
    prompt = input("Enter your research topic or question: ").strip()

    if not prompt:
        prompt = "Give me 5 fun and fascinating facts about tardigrades."
        print(f"No prompt entered. Using default: {prompt}")
    
    # The input data for your Workflow, including the prompt and API key
    research_input = GenerateReportInput(prompt=prompt)
    
   # Start the Workflow execution
    handle = await client.start_workflow(
        GenerateReportWorkflow.run, # The Workflow method to execute
        research_input,
        id=f"generate-researdch-report-workflow-{uuid.uuid4()}",
        task_queue="research", # task queue your Worker is polling
    )

    print(f"Started workflow. Workflow ID: {handle.id}, RunID {handle.result_run_id}")
    result = await handle.result()
    print(f"Result: {result}")
    
if __name__ == "__main__":
    asyncio.run(main()) 