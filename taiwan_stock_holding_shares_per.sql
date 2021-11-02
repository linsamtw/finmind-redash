SELECT taiwan_stock_holding_shares_per.date AS date,
       SUM(taiwan_stock_holding_shares_per.unit) AS "大戶持股數量"
FROM `taiwan_stock_holding_shares_per` AS taiwan_stock_holding_shares_per
INNER JOIN taiwan_stock_info AS taiwan_stock_info ON taiwan_stock_info.stock_id =taiwan_stock_holding_shares_per.stock_id
WHERE taiwan_stock_info.stock_name = '{{股票名稱}}'
  AND taiwan_stock_holding_shares_per.date >= '{{date.start}}'
  AND taiwan_stock_holding_shares_per.date <= '{{date.end}}'
  AND taiwan_stock_holding_shares_per.HoldingSharesLevel NOT IN('1-999',
                                                                'total')
GROUP BY date;