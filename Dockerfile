FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY templates ./templates
COPY static ./static
COPY prompts/system_brujula_v1_7.txt ./prompts/
COPY data/catalogo_demo_v3.json data/glosario_v1.json data/historico_categorias_v1.json ./data/
RUN useradd --create-home brujula && chown -R brujula /app
USER brujula
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request,os; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT','8000'))" || exit 1
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips='*'"]
