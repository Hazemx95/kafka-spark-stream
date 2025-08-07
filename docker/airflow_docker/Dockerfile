FROM apache/airflow:2.8.0

USER root
RUN apt-get update && apt-get install -y 
RUN apt install openssh-server curl wget -y

USER airflow
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-spark \
    apache-airflow-providers-postgres \
    apache-airflow-providers-docker \
    apache-airflow-providers-vertica