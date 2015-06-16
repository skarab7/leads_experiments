############################################################
# 1. Clone https://github.com/amplab/benchmark.git
# 2. Copy the extract_sql_queries.py to benchmark/runner
# 3. run: python extract_sql_queries
############################################################
import sys


class MockPg8000:
    """
    """
    DBAPI = ""


sys.modules['pg8000'] = MockPg8000()

import run_query

qs = ['QUERY_1a_SQL',
      'QUERY_1b_SQL',
      'QUERY_1c_SQL',
      'QUERY_2a_SQL',
      'QUERY_2b_SQL',
      'QUERY_2c_SQL',
      'QUERY_3a_SQL',
      'QUERY_3b_SQL',
      'QUERY_3c_SQL']

create_queries = ['QUERY_1_PRE',
                  'QUERY_2_PRE',
                  'QUERY_3_PRE']


print("\n###### create table from queries ######")
for k, v in run_query.QUERY_MAP.iteritems():
    q = v[2]
    if q:
        print("### {0} ####".format(k))
        print q

print("###############################")
print("#####  extracted          #####")
print("###############################")
print("###### benchmark queries ######")
for q in qs:
    print("### {0} ####".format(q))
    print(getattr(run_query, q))

print("\n###### clean queries ######")
print(run_query.CLEAN_QUERY)

print("\n###### create table queries ######")
for c_q in create_queries:
    print("### {0} ####".format(c_q))
    print(getattr(run_query, c_q))
