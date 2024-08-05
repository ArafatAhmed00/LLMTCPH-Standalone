WITH revenue AS (
    SELECT
        l_suppkey AS supplier_no,
        SUM(l_extendedprice * (1 - l_discount)) AS total_revenue
    FROM
        lineitem
    WHERE
        l_shipdate >= '1996-01-01'
        AND l_shipdate < date('1996-01-01', '+3 months')
    GROUP BY
        l_suppkey
)
SELECT
    s.s_suppkey,
    s.s_name,
    s.s_address,
    s.s_phone,
    r.total_revenue
FROM
    supplier s
JOIN revenue r ON s.s_suppkey = r.supplier_no
WHERE
    r.total_revenue = (SELECT MAX(total_revenue) FROM revenue)
ORDER BY
    s.s_suppkey;
