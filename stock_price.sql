SELECT stock_price.Close AS '股價',
       stock_price.TradeVolume AS "交易量",
       stock_price.date AS date
FROM taiwan_stock_price AS stock_price
INNER JOIN taiwan_stock_info AS si ON si.stock_id = stock_price.StockID
WHERE si.stock_name = '{{股票名稱}}'
  AND stock_price.date >= '{{date.start}}'
  AND stock_price.date <= '{{date.end}}'