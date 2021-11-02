SELECT stock_price.close AS '股價',
       stock_price.Trading_Volume AS "交易量", 大戶持股數量, stock_price.date AS date
FROM taiwan_stock_price AS stock_price
INNER JOIN taiwan_stock_info AS si ON si.stock_id = stock_price.stock_id
INNER JOIN
  ( SELECT tshsp.stock_id AS stock_id,
           tshsp.date AS date,
           SUM(tshsp.unit) AS "大戶持股數量"
   FROM `taiwan_stock_holding_shares_per` AS tshsp
   INNER JOIN taiwan_stock_info AS taiwan_stock_info ON taiwan_stock_info.stock_id =tshsp.stock_id
   WHERE taiwan_stock_info.stock_name = '{{股票名稱}}'
     AND tshsp.date >= '{{date.start}}'
     AND tshsp.date <= '{{date.end}}'
     AND tshsp.HoldingSharesLevel NOT IN('1-999',
                                         'total')
   GROUP BY stock_id, date ) AS taiwan_stock_holding_shares_per 
   ON taiwan_stock_holding_shares_per.stock_id = stock_price.stock_id
   AND taiwan_stock_holding_shares_per.date = stock_price.date
WHERE si.stock_name = '{{股票名稱}}'
  AND stock_price.date >= '{{date.start}}'
  AND stock_price.date <= '{{date.end}}'