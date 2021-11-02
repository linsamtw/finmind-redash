

create-postgres-volume:
	docker volume create --name=postgres

create-redis-redash-volume:
	docker volume create --name=redis_redash

create-db:
	docker-compose run --rm server create_db

create-db-by-python:
	# docker exec -it redash_server_1 bash
	python /app/manage.py database create_tables

up:
	docker-compose -f docker-compose.yml up

up-d:
	docker-compose -f docker-compose.yml up -d

down:
	docker-compose -f docker-compose.yml down

# test
test-cov:
	pipenv run pytest --cov-report term-missing --cov-config=.coveragerc --cov=./${PROJECT_NAME}/ tests/

test:
	pipenv run pytest

# other
format:
	black -l 80 redash/* tests/* example/*

download-taiwan-stock-info:
	python3 upload_data2mysql.py taiwan_stock_info

download-taiwan-stock-price:
	python3 upload_data2mysql.py taiwan_stock_price 2330 2615 2603 2609

download-taiwan-stock-institutional-investors:
	python3 upload_data2mysql.py taiwan_stock_institutional_investors 2330 2615 2603 2609

download-taiwan-stock-margin-purchase-short_sale:
	python3 upload_data2mysql.py taiwan_stock_margin_purchase_short_sale 2330 2615 2603 2609

download-taiwan-stock-holding-shares-per:
	python3 upload_data2mysql.py taiwan_stock_holding_shares_per 2330 2615 2603 2609

