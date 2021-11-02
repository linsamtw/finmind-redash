import os
import sys

import pandas as pd
from loguru import logger
from sqlalchemy import (
    create_engine,
    engine,
)
from tqdm import tqdm
import pymysql

from FinMind.data import DataLoader


def get_mysql_financialdata_conn() -> engine.base.Connection:
    # TODO 請將 IP 換成讀者自己的 IP
    address = "mysql+pymysql://root:test@127.0.0.1:3306/FinancialData"
    engine = create_engine(address)
    connect = engine.connect()
    return connect


def create_taiwan_stock_info_sql():
    return """
        CREATE TABLE `taiwan_stock_info` (
            `industry_category` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `stock_id` varchar(32) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
            `stock_name` varchar(30) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
            `type` varchar(4) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '上市twse/上櫃tpex',
            `date` date DEFAULT NULL,
            PRIMARY KEY (`stock_id`,`industry_category`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci;
    """


def create_taiwan_stock_price_sql():
    return """
        CREATE TABLE `taiwan_stock_price` (
            `stock_id` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
            `Trading_turnover` bigint NOT NULL,
            `Trading_Volume` int NOT NULL,
            `Trading_money` bigint NOT NULL,
            `open` float NOT NULL,
            `max` float NOT NULL,
            `min` float NOT NULL,
            `close` float NOT NULL,
            `spread` float NOT NULL,
            `date` date NOT NULL,
            PRIMARY KEY(`stock_id`, `date`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8_unicode_ci
        PARTITION BY KEY (stock_id)
        PARTITIONS 10;
    """


def create_taiwan_stock_institutional_investors_sql():
    return """
        CREATE TABLE taiwan_stock_institutional_investors(
            `name` VARCHAR(20),
            `buy` BIGINT(64),
            `sell` BIGINT(64),
            `stock_id` VARCHAR(10),
            `date` DATE,
            PRIMARY KEY(`stock_id`, `date`, `name`)
        ) PARTITION BY KEY(`stock_id`) PARTITIONS 10;
    """


def create_taiwan_stock_margin_purchase_short_sale_sql():
    return """
        CREATE TABLE `taiwan_stock_margin_purchase_short_sale`(
            `stock_id` VARCHAR(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL COMMENT '股票代碼',
            `MarginPurchaseBuy` BIGINT NOT NULL COMMENT '融資買進',
            `MarginPurchaseSell` BIGINT NOT NULL COMMENT '融資賣出',
            `MarginPurchaseCashRepayment` BIGINT NOT NULL COMMENT '融資現金償還',
            `MarginPurchaseYesterdayBalance` BIGINT NOT NULL COMMENT '融資昨日餘額',
            `MarginPurchaseTodayBalance` BIGINT NOT NULL COMMENT '融資今日餘額',
            `MarginPurchaseLimit` BIGINT NOT NULL COMMENT '融資限額',
            `ShortSaleBuy` BIGINT NOT NULL COMMENT '融券買進',
            `ShortSaleSell` BIGINT NOT NULL COMMENT '融券賣出',
            `ShortSaleCashRepayment` BIGINT NOT NULL COMMENT '融券償還',
            `ShortSaleYesterdayBalance` BIGINT NOT NULL COMMENT '融券昨日餘額',
            `ShortSaleTodayBalance` BIGINT NOT NULL COMMENT '融券今日餘額',
            `ShortSaleLimit` BIGINT NOT NULL COMMENT '融券限制',
            `OffsetLoanAndShort` BIGINT DEFAULT NULL COMMENT '資券互抵',
            `date` DATE NOT NULL COMMENT '日期',
            `Note` VARCHAR(10) CHARACTER SET utf8 COLLATE utf8_unicode_ci COMMENT 'Note',
            PRIMARY KEY(`stock_id`, `date`)
        ) PARTITION BY KEY(`stock_id`) PARTITIONS 10;
    """


def create_taiwan_stock_holding_shares_per_sql():
    return """
        CREATE TABLE taiwan_stock_holding_shares_per (
            `HoldingSharesLevel` VARCHAR(19),
            `people` INT(10),
            `unit` BIGINT(64),
            `percent` FLOAT,
            `stock_id` VARCHAR(10),
            `date` DATE,
            `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (`stock_id`,`date`,`HoldingSharesLevel`)
        )
        PARTITION BY KEY(stock_id)
        PARTITIONS 10;
    """


def create_table(table: str):
    mysql_conn = get_mysql_financialdata_conn()
    sql = eval(f"create_{table}_sql()")
    try:
        logger.info(f"create table {table}")
        mysql_conn.execute(sql)
    except:
        logger.info(f"{table} already exists")


def build_update_sql(colname, value):
    update_sql = ",".join(
        [
            ' `{}` = "{}" '.format(colname[i], str(value[i]))
            for i in range(len(colname))
            if str(value[i])
        ]
    )
    return update_sql


def build_df_update_sql(table, df):
    logger.info("build_df_update_sql")
    df_columns = list(df.columns)
    sql_list = []
    for i in range(len(df)):
        temp = list(df.iloc[i])
        value = [pymysql.converters.escape_string(str(v)) for v in temp]
        sub_df_columns = [df_columns[j] for j in range(len(temp))]
        update_sql = build_update_sql(sub_df_columns, value)
        sql = """INSERT INTO `{}`({})VALUES ({}) ON DUPLICATE KEY UPDATE {}
            """.format(
            table,
            "`{}`".format("`,`".join(sub_df_columns)),
            '"{}"'.format('","'.join(value)),
            update_sql,
        )
        sql_list.append(sql)
    return sql_list


def df_update2mysql(df, table, mysql_conn):
    sql = build_df_update_sql(table, df)
    commit(sql=sql, mysql_conn=mysql_conn)


def commit(
    sql,
    mysql_conn,
):
    logger.info("commit")
    try:
        trans = mysql_conn.begin()
        if isinstance(sql, list):
            for s in sql:
                try:
                    mysql_conn.execution_options(autocommit=False).execute(s)
                except Exception as e:
                    logger.info(e)
                    logger.info(s)
                    break

        elif isinstance(sql, str):
            mysql_conn.execution_options(autocommit=False).execute(sql)
        trans.commit()
    except Exception as e:
        trans.rollback()
        logger.info(e)


def upload_data2mysql(table, stock_id_list):
    api = DataLoader()
    # api.login_by_token(api_token='token')
    mysql_conn = get_mysql_financialdata_conn()
    for stock_id in stock_id_list:
        if table == "taiwan_stock_holding_shares_per":
            df = api.taiwan_stock_holding_shares_per(
                stock_id=stock_id,
                start_date="2000-01-01",
                end_date="2021-11-01",
            )
        elif table == "taiwan_stock_price":
            df = api.taiwan_stock_daily(
                stock_id=stock_id,
                start_date="2000-01-01",
                end_date="2021-11-01",
            )
        elif table == "taiwan_stock_margin_purchase_short_sale":
            df = api.taiwan_stock_margin_purchase_short_sale(
                stock_id=stock_id,
                start_date="2000-01-01",
                end_date="2021-11-01",
            )
        elif table == "taiwan_stock_institutional_investors":
            df = api.taiwan_stock_institutional_investors(
                stock_id=stock_id,
                start_date="2000-01-01",
                end_date="2021-11-01",
            )
        df_update2mysql(
            df=df,
            table=table,
            mysql_conn=mysql_conn,
        )


def main(table, stock_id_list):
    create_table(
        table=table,
    )
    upload_data2mysql(table, stock_id_list)


if __name__ == "__main__":
    table = sys.argv[1]
    stock_id_list = sys.argv[2:]
    main(table, stock_id_list)
