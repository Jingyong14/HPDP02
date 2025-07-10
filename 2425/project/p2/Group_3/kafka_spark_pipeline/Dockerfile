# Dockerfile

FROM bitnami/spark:3.5.0

USER root

WORKDIR /opt/spark-apps

# Copy your code
COPY ./scripts ./scripts
COPY ./model ./model
COPY ./output ./output
COPY ./data ./data

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
        pyarrow>=12.0.0 \
        pandas \
        scikit-learn \
        joblib \
        kafka-python \
        newspaper3k \
        nltk \
        elasticsearch \
        beautifulsoup4 \
        requests \
        py4j && \
    python3 -c "import nltk; \
                nltk.download('punkt'); \
                nltk.download('stopwords'); \
                nltk.download('wordnet'); \
                nltk.download('punkt_tab')"


# Bitnami's default entrypoint needs SPARK_MODE
ENV PYSPARK_PYTHON=python3
ENTRYPOINT [ "/opt/bitnami/scripts/spark/entrypoint.sh" ]
CMD [ "/opt/bitnami/scripts/spark/run.sh" ]
