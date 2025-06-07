FROM mysql:5.7

ENV MYSQL_ROOT_PASSWORD=1234

WORKDIR /

# 초기 데이터베이스 환경 구성 시 필요함
ADD init-db.sh /docker-entrypoint-initdb.d

CMD ["mysqld"]