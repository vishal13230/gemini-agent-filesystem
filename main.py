import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

BASE = "agent_fs"
os.makedirs(BASE, exist_ok=True)

MEMORY_FILE = f"{BASE}/memory.json"
LOG_FILE = f"{BASE}/logs.txt"


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}

    with open(MEMORY_FILE) as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)


def search_web(query):

    url = f"https://api.duckduckgo.com/?q={query}&format=json"

    r = requests.get(url).json()

    result = r.get("AbstractText")

    if not result:
        result = "No summary found"

    log(f"Search used for: {query}")

    return result


def think(prompt):

    response = model.generate_content(prompt)

    return response.text


def run_agent(query):

    log(f"New task: {query}")

    memory = load_memory()

    plan_prompt = f"""
You are an AI research assistant.

Question:
{query}

Should we search the web?

Format:
SEARCH: yes/no
"""

    plan = think(plan_prompt)

    print("\nPLAN\n", plan)

    context = ""

    if "yes" in plan.lower():

        context = search_web(query)

        print("\nSEARCH RESULT\n", context)

    final_prompt = f"""
Question:
{query}

Memory:
{memory}

Search Context:
{context}

Give a clear structured answer.
"""

    answer = think(final_prompt)

    print("\nANSWER\n", answer)

    memory[query] = answer[:200]

    save_memory(memory)

    log("Task completed")


if __name__ == "__main__":

    q = input("Ask something: ")

    run_agent(q)