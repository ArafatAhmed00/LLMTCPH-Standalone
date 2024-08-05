WITH avg_quantities AS (
    SELECT l_partkey, 0.2 * AVG(l_quantity) AS avg_qty
    FROM lineitem
    GROUP BY l_partkey
)
SELECT SUM(l.l_extendedprice) / 7.0 AS avg_yearly
FROM lineitem l
INNER JOIN part p ON p.p_partkey = l.l_partkey
INNER JOIN avg_quantities aq ON aq.l_partkey = l.l_partkey
WHERE p.p_brand = 'Brand#23'
	AND p.p_container = 'MED BOX'
	AND l.l_quantity < aq.avg_qty;