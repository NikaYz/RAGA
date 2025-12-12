# evaluation/evaluation.py
import requests
import pandas as pd
import asyncio
import time

from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory
from ragas.metrics.collections import Faithfulness, AnswerRelevancy

from test_bed import test_bed


API_URL = "http://localhost:8000/query"


def query_rag(question):
    payload = {"query": question}
    response = requests.post(API_URL, json=payload).json()
    return response["answer"], response["sources"]


def load_eval_questions():
    return test_bed


async def score_item(llm, embeddings, question, answer, contexts):
    """
    Score one sample using the EXACT 'ascore' method from docs.
    """

    # create metrics exactly like docs
    faith_scorer = Faithfulness(llm=llm)
    relev_scorer = AnswerRelevancy(llm=llm, embeddings=embeddings)

    # run metrics
    faith_res = await faith_scorer.ascore(
        user_input=question,
        response=answer,
        retrieved_contexts=contexts
    )

    relev_res = await relev_scorer.ascore(
        user_input=question,
        response=answer
    )

    return faith_res.value, relev_res.value


async def main():
    # -------------------------------------------------------
    # 1. SETUP LLM AND EMBEDDINGS (exactly like documentation)
    # -------------------------------------------------------
    client = AsyncOpenAI()

    llm = llm_factory("gpt-4o-mini", client=client)

    embeddings = embedding_factory(
        "openai",
        model="text-embedding-3-small",
        client=client,
        interface="modern"
    )

    # -------------------------------------------------------
    # 2. Load questions and start evaluation
    # -------------------------------------------------------
    data = load_eval_questions()

    results = []

    print("Running low-level Ragas metrics...\n")

    for item in data[:2]:
        question = item["question"]
        answer, contexts = query_rag(question)

        print(f"Evaluating: {question}")
        print("WAIT 2 SEC...")
        time.sleep(2)
        print("BACK ON")

        # ---------------------------------------------------
        # 3. Score one item using low-level ascore()
        # ---------------------------------------------------
        faith, relev = await score_item(
            llm, embeddings,
            question, answer, contexts
        )

        results.append({
            "question": question,
            "answer": answer,
            "contexts": contexts,
            "faithfulness": faith,
            "answer_relevancy": relev
        })

        print(f"Faithfulness = {faith:.4f}, AnswerRelevancy = {relev:.4f}\n")

    # -------------------------------------------------------
    # 4. Save results CSV
    # -------------------------------------------------------
    df = pd.DataFrame(results)
    df.to_csv("evaluation_results.csv", index=False)

    print("\n=== Final Scores ===")
    print(df[["question", "faithfulness", "answer_relevancy"]])

    print("\nSaved evaluation_results.csv")


if __name__ == "__main__":
    asyncio.run(main())
