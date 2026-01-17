import asyncio
import concurrent.futures

from temporal.activities import create_pdf, llm_call
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.worker import Worker
from temporal.workflow import GenerateReportWorkflow


async def run_worker():
    # Connect to Temporal service
    client = await Client.connect(
        "localhost:7233",
        namespace="default",
        data_converter=pydantic_data_converter,
    )

    # Create a thread pool for running Activities
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as activity_executor:
        # Configure the Worker
        worker = Worker(
            client,
            task_queue="research",  # Task queue that your Worker is listening to.
            workflows=[GenerateReportWorkflow],  # Register the Workflow on your Worker
            activities=[llm_call, create_pdf],  # Register the Activities on your Worker
            activity_executor=activity_executor,  # Thread pool that allows Activities to run concurrently
        )

        print("Starting the worker....")
        await worker.run()


if __name__ == "__main__":
    asyncio.run(run_worker())
