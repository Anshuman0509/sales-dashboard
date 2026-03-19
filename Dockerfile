FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]


Also update `requirements.txt`:

pandas==2.2.2
plotly==5.18.0
streamlit==1.38.0
google-genai==1.68.0
python-dotenv==1.0.1
