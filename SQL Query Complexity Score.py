import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

def is_subselect(parsed):
    if not parsed.is_group:
        return False
    for item in parsed.tokens:
        if item.ttype is Keyword and item.value.upper() in ('SELECT', 'WITH'):
            return True
    return False

def extract_from_part(parsed):
    from_seen = False
    for item in parsed.tokens:
        if from_seen:
            if is_subselect(item):
                yield from extract_from_part(item)
            elif item.ttype is Keyword:
                return
            else:
                yield item
        elif item.ttype is Keyword and item.value.upper() == 'FROM':
            from_seen = True

def extract_tables(sql):
    extracted_tables = set()
    parsed = sqlparse.parse(sql)
    for item in parsed[0].tokens:
        if item.ttype is DML and item.value.upper() == 'SELECT':
            for x in extract_from_part(parsed[0]):
                if isinstance(x, IdentifierList):
                    for identifier in x.get_identifiers():
                        extracted_tables.add(identifier.get_real_name())
                elif isinstance(x, Identifier):
                    extracted_tables.add(x.get_real_name())
    return extracted_tables

def complexity_score(sql):
    score = 0
    parsed = sqlparse.parse(sql)[0]
    joins = sum(1 for token in parsed.tokens if token.value.upper() == 'JOIN')
    subqueries = sum(1 for token in parsed.tokens if is_subselect(token))
    conditions = sum(1 for token in parsed.tokens if token.ttype is Keyword and token.value.upper() in ('WHERE', 'AND', 'OR'))
    group_by = sum(1 for token in parsed.tokens if token.ttype is Keyword and token.value.upper() == 'GROUP BY')
    having = sum(1 for token in parsed.tokens if token.ttype is Keyword and token.value.upper() == 'HAVING')
    order_by = sum(1 for token in parsed.tokens if token.ttype is Keyword and token.value.upper() == 'ORDER BY')

    score += joins * 2
    score += subqueries * 3
    score += conditions
    score += group_by * 2
    score += having * 2
    score += order_by

    return score

# Example usage
sql_query = """
select
    l_returnflag,
    l_linestatus,
    sum(l_quantity) as sum_qty,
    sum(l_extendedprice) as sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) as sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge,
    avg(l_quantity) as avg_qty,
    avg(l_extendedprice) as avg_price,
    avg(l_discount) as avg_disc,
    count(*) as count_order
from
    lineitem
where
    l_shipdate <= date('1998-12-01', '-90 days')
group by
    l_returnflag,
    l_linestatus
order by
    l_returnflag,
    l_linestatus;
"""

print("Complexity Score:", complexity_score(sql_query))



