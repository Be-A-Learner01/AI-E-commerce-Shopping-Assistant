from agent.prompts import CONFLICT_PROMPTS
from utils.llm import invoke_llm_with_timeout
from models.llm import conflict_model
from langchain_core.messages import SystemMessage
import time

async def detect_memory_conflict(existing_memory:str,new_memory:str) -> bool:

    prompts = CONFLICT_PROMPTS.format(
        existing_memory=existing_memory,
        new_memory=new_memory

    )
    start = time.perf_counter()
    resposne = await invoke_llm_with_timeout(
        conflict_model,
        [
            SystemMessage(content=prompts)
        ]
    )
    elapsed = time.perf_counter() - start
    print(f"=== LLM Latency === conflict: {elapsed:.2f}s")
    return resposne.conflict == "yes"