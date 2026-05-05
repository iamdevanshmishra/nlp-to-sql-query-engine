import os
import sqlite3
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# ------------------ LLM → SQL ------------------
from dotenv import load_dotenv
load_dotenv()

def get_sql_query(user_query):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY is missing! Set it in your .env file."

    groq_sys_prompt = ChatPromptTemplate.from_template("""
You are a professional data analyst.

You are working with a SQLite database that has one table named STUDENT
with the following columns:
id, first_name, last_name, course, section, marks, exam_date.

Your task:
- Convert the user's question into a valid SQL SELECT query
- Use aggregation functions such as COUNT, AVG, SUM, MAX, or MIN when appropriate
- Use GROUP BY for analytical comparisons
- Use only the columns listed above
- Do NOT generate INSERT, UPDATE, DELETE, DROP, or ALTER statements
- Return ONLY the SQL query, without any explanation or formatting

Question: {user_query}
""")

    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant"
    )

    chain = groq_sys_prompt | llm | StrOutputParser()
    return chain.invoke({"user_query": user_query})

# ------------------ SQL → DataFrame ------------------
def return_sql_response(sql_query):
    try:
        with sqlite3.connect("student.db") as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        return str(e)

# ------------------ Visualization ------------------
def plot_insights(df, chart_type="Auto"):
    if df.shape[1] == 2:
        x_col, y_col = df.columns

        fig, ax = plt.subplots()

        if chart_type == "Line Chart":
            sns.lineplot(data=df, x=x_col, y=y_col, ax=ax)
            ax.set_title("Line Chart")

        elif chart_type == "Bar Chart":
            sns.barplot(data=df, x=x_col, y=y_col, ax=ax)
            ax.set_title(f"{y_col} by {x_col}")

        else:  # Auto mode
            try:
                df[x_col] = pd.to_datetime(df[x_col])
                sns.lineplot(data=df, x=x_col, y=y_col, ax=ax)
                ax.set_title("Trend Over Time")
            except:
                sns.barplot(data=df, x=x_col, y=y_col, ax=ax)
                ax.set_title(f"{y_col} by {x_col}")

        plt.xticks(rotation=45)
        st.pyplot(fig)

    else:
        st.info("Visualization not supported for this query.")

# ------------------ Streamlit UI ------------------
def main():
    st.set_page_config(page_title="QuerySense", layout="centered")
    st.title("AnalytIQ")

    # -------- HELP SECTION --------
    with st.sidebar:
        st.title("Help")
        st.subheader("💡 What you can do:")
        st.markdown("""
- Ask analytical questions on the STUDENT table  
- Use queries like: average marks, total students, highest/lowest marks  
- Compare results by course or section  
- Get results as a table and bar/line charts  
        """)

    user_query = st.text_input("Ask your question:")
    submit = st.button("Run Query")

    if submit and user_query:

        sql_query = get_sql_query(user_query)

        if sql_query.startswith("Error:"):
            st.error(sql_query)
            return

        st.subheader("🧾 Generated SQL")
        st.code(sql_query, language="sql")

        if not sql_query.lower().strip().startswith("select"):
            st.error("Only SELECT queries are allowed.")
            return

        df = return_sql_response(sql_query)

        if isinstance(df, str):
            st.error(df)

        elif df.empty:
            st.warning("No data found.")

        else:
            st.subheader("📊 Results")
            st.dataframe(df)

            # 🔥 Chart selection
            chart_type = st.selectbox(
                "Choose Visualization",
                ["Auto", "Bar Chart", "Line Chart"]
            )

            st.subheader("📈 Visual Insights")
            plot_insights(df, chart_type)


if __name__ == "__main__":
    main()