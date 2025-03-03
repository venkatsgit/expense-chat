from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import uvicorn
import pymysql
import urllib.parse
import re
from operator import itemgetter
from huggingface_hub import InferenceClient
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from sqlalchemy.exc import SQLAlchemyError
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

# Initialize FastAPI app
app = FastAPI()

# Set Hugging Face API token securely
os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

# Database connection details
db_user = "root"
db_password = urllib.parse.quote("test@123")
db_host = "localhost"
db_name = "expensive"

# Define the table to use
select_table = ["transactions"]

# Initialize SQL Database
try:
    db = SQLDatabase.from_uri(f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
                              include_tables=select_table)
    print("Database connected successfully.")
except SQLAlchemyError as e:
    print(f"Database connection error: {e}")
    exit()

# Initialize Hugging Face Inference Client
client = InferenceClient("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3")

class QuestionRequest(BaseModel):
    question: str
    userID: str

# Function to generate a valid SQL query
def generate_sql_query(question):
    try:
        schema_info = """
           The database has a table named 'transactions' with the following columns:
           - id (integer, primary key)
           - category (varchar)
           - amount (decimal)
           - expensive_date (date)

           Generate ONLY the SQL query based on this table.
           """

        prompt = f"{schema_info}\n\n{question}"
        response = client.text_generation(prompt)
        response = response.strip()

        # Extract only the SQL query using regex
        sql_match = re.search(r"```sql\s+(.*?)\s+```", response, re.DOTALL)
        if sql_match:
            sql_query = sql_match.group(1).strip()
        else:
            sql_query = response  # If no ```sql``` wrapper is found, assume response is the query

        # Basic validation
        if not sql_query.lower().startswith("select"):
            raise ValueError("Generated response is not a valid SQL query.")

        return sql_query
    except Exception as e:
        print(f"Error generating SQL query: {e}")
        return None

# Function to execute SQL query
def execute_sql_query(query):
    execute_query = QuerySQLDatabaseTool(db=db)
    try:
        result = execute_query.invoke(query)
        return result
    except SQLAlchemyError as e:
        print(f"Error executing SQL query: {e}")
        return None

# Wrap Hugging Face client in a LangChain Runnable
def query_huggingface(input_text):
    """Ensure the input is a plain string before sending it to Hugging Face."""
    if not isinstance(input_text, str):
        input_text = str(input_text)
    return client.text_generation(input_text)

llm_runnable = RunnableLambda(query_huggingface)

# Answer rephrasing prompt
answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)

# LangChain pipeline for query execution and rephrasing
def process_question(question):
    query = generate_sql_query(question)

    if query:
        print(f"Generated SQL Query:\n{query}")
        result = execute_sql_query(query)

        if result:
            # Rephrase the answer
            rephrase_answer = answer_prompt | llm_runnable | StrOutputParser()
            answer = rephrase_answer.invoke({"question": question, "query": query, "result": result})
            return answer
        else:
            return "SQL execution failed."
    else:
        return "Failed to generate a valid SQL query."

@app.post("/chatbot")
def chatbot_endpoint(request: QuestionRequest):
    answer = process_question(request.question)
    return {"userID": request.userID, "question": request.question, "answer": answer}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
