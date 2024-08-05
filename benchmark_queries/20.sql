WITH date_range AS (
	SELECT 
		date('1994-01-01') AS start_date,
		date('1994-01-01', '+1 year') AS end_date
),
quantity_summary AS (
	SELECT 
		l_partkey,
		l_suppkey,
		0.5 * SUM(l_quantity) AS half_sum_quantity
	FROM 
		lineitem, date_range
	WHERE 
		l_shipdate >= date_range.start_date
		AND l_shipdate < date_range.end_date
	GROUP BY 
		l_partkey, l_suppkey
)
SELECT DISTINCT
	s.s_name,
	s.s_address
FROM 
	supplier s
JOIN 
	nation n ON s.s_nationkey = n.n_nationkey
JOIN 
	partsupp ps ON s.s_suppkey = ps.ps_suppkey
JOIN 
	part p ON ps.ps_partkey = p.p_partkey
JOIN 
	quantity_summary qs ON ps.ps_partkey = qs.l_partkey AND ps.ps_suppkey = qs.l_suppkey
WHERE 
	n.n_name = 'CANADA'
	AND p.p_name LIKE 'forest%'
	AND ps.ps_availqty > qs.half_sum_quantity
ORDER BY 
	s.s_name;