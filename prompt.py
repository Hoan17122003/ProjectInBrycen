from langchain_core.prompts.prompt import PromptTemplate
CYPHER_GENERATION_TEMPLATE = """
Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:
{schema}
Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
The generated statement will list all nodes, relationships related to the entity mentioned in the question.
The entity in the question may not exist in the Schema, try to bring these entities to the synonym entity in the schema if there is.
---Example---
Excample1:
"question": "Who is Tran Huu Trung?"
"query": "MATCH (n )-[r]-(m) WHERE (toLower(n.id) contains "trần hữu trung") RETURN n, r, m"

Excample1:
"question": "What information is available about Company XYZ?"
"query" : "MATCH (n:Company) WHERE toLower(n.name) = "company xyz" 
OPTIONAL MATCH (n)-[r]->(m)
RETURN n, r, m"

-Use relationships up to 2 [r*..2], no more
-Prioritize query cyphers that output more information

The question is:
{question}

Important note: users may have misspelled the word, please correct it before proceeding to create Cypher query
"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)


# -User input may not fit into the schema, try to convert it to types in the Schema