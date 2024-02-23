FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY src/requirements.txt /tmp/requirements.txt
COPY src/api .

RUN pip install -r /tmp/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "3"]