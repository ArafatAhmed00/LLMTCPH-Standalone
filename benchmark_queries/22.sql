WITH avg_balance AS (
    SELECT AVG(c_acctbal) as avg_acctbal
    FROM customer
    WHERE c_acctbal > 0.00
    AND substr(c_phone, 1, 2) IN ('13', '31', '23', '29', '30', '18', '17')
),
potential_customers AS (
    SELECT 
        substr(c_phone, 1, 2) as cntrycode,
        c_acctbal,
        c_custkey
    FROM customer
    WHERE substr(c_phone, 1, 2) IN ('13', '31', '23', '29', '30', '18', '17')
),
customers_without_orders AS (
    SELECT pc.cntrycode, pc.c_acctbal
    FROM potential_customers pc
    LEFT JOIN orders o ON o.o_custkey = pc.c_custkey
    WHERE o.o_custkey IS NULL
)
SELECT
    cntrycode,
    COUNT(*) as numcust,
    SUM(c_acctbal) as totacctbal
FROM customers_without_orders, avg_balance
WHERE c_acctbal > avg_acctbal
GROUP BY cntrycode
ORDER BY cntrycode;
