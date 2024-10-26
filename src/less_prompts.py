from enum import Enum


NEW_RULE_TAG = ['<New Rule>', '</New Rule>']


class RuleGenerationPrompts(Enum):
    SYSTEM_PROMPT = lambda: '''You are an expert SQL engineer with 20+ years of experience. You will be given some SQL equivalence rules conditional on some database schemas. You will then be given a pair of SQL queries, consisting of a gold query and a machine-generated query, and a database schema that defines the context of the queries. 

Your task is to compare the two provided SQL queries on logical equivalence and generate one more equivalence rule in the same format as the provided example equivalence rules.

Please make sure you read and understand these instructions carefully. Please also keep this document open while reviewing, and refer to it as needed.



Evaluation Criteria:

Logical equivalence - the alignment between the gold SQL query and the machine-generated SQL query. A machine-generated SQL query is logically equivalent to the gold query if these two queries would RETURN THE SAME RESULTS AND IN THE SAME ORDER for ALL POSSIBLE DATABASE INSTANCES that satisfy the provided database schema for these queries. Annotators were asked to penalize machine-generated queries that overlooked edge cases that the gold queries would have caught otherwise.



Evaluation steps:

1. Understand the Database Schema: Identify all tables used in both queries. List all columns referenced, along with their data types and constraints. Determine primary and foreign key relationships. Note any indexes or unique constraints that may affect query execution.
2. Parse and Break Down Each Query: Identify selected columns, functions, and expressions. Note the tables involved and the join conditions. Understand the filtering conditions applied. Identify grouping and aggregate conditions, if any. Determine if result ordering affects equivalence.
3. Compare Query Components: Check if both queries use the same tables and join conditions. Compare filtering conditions in the WHERE clauses. Assess whether the same columns and expressions are selected. Identify if different functions or syntaxes achieve the same result. Look for logical equivalence in expressions and calculations.
4. Consider Edge Cases and Data Variations: Conceptualize sample datasets that include edge cases (e.g., NULL values, zero values, special characters). Analyze how each query handles these edge cases. Ensure that data type differences do not affect the outcome. Verify that constraints (e.g., NOT NULL, UNIQUE) are accounted for.
5. Evaluate Aggregations and Calculations: Confirm that aggregate functions (e.g., SUM, COUNT) are applied identically. Ensure calculations (e.g., subtraction, addition) produce the same results.
6. Check for Logical Equivalence in Conditional Expressions: Compare conditional expressions like IIF, CASE WHEN, and IF. Determine if conditions and returned values are logically the same.
7. Assess Ordering of Results: If ORDER BY clause is present, confirm that both queries order results identically. Recognize that differing order may affect equivalence if result order is significant.
8. Generate a New Logical Equivalence Rule (If Applicable): Create an "Equivalent Queries: <query1>\n<query2>\nSchema Conditions:<conditions>" statement that defines the equivalence. Use GENERALIZED COLUMN and TABLE NAMES. Specify any necessary conditions based on the database schema. Present the rule clearly, indicating both the equivalence and the conditions under which it holds.'''
    
    
    EXAMPLE_RULES = lambda rules: 'Example Equivalence Rules:\n\n' + '\n\n'.join([f'<Rule{i+1}>\n{rule}\n</Rule{i+1}>' for i, rule in enumerate(rules)])
    
    
    GUIDELINES = lambda: f'''# Guidelines:
- Make SURE complete to every step PERFECTLY without ANY Mistakes
- Follow the Rules I Gave you and Remember to AVOID generating repeated equivalence rules in the examples I gave you.
- Be sure to format your response like the example equivalence rules I gave you.
- Put {''.join(NEW_RULE_TAG)} around the new equivalence rule that you think of. Do not use other formatting around the equivalent queries.
- Use GENERALIZED COLUMN AND TABLE NAMES in any EQUIVALENCE RULE YOU WRITE.
- If the two queries are not logically equivalent, say {NEW_RULE_TAG[0]}Not equivalent{NEW_RULE_TAG[1]}.

Take a Deep Breath and Carefully Follow the Rules, Guides and Examples I gave you. I will tip you $2000 if you do EVERYTHING Perfectly.'''
    

    QUERY = lambda schema, gold, machine: f'''Pair of SQL Queries:
<Gold SQL Query>
{gold.strip().strip(';')+';'}
</Gold SQL Query>

<Machine-generated SQL Query>
{machine.strip().strip(';')+';'}
</Machine-generated SQL Query>

<Schema Creation Queries>
{schema.strip()}
</Schema Creation Queries>'''


    ESM_P_RULES = lambda: [
'''Equivalent Queries:
SELECT _ FROM t1 WHERE c1 = (SELECT MIN/MAX(c1) FROM t1);
SELECT _ FROM t1 ORDER BY c1 ASC/DESC LIMIT 1;
Schema Conditions:
c1 is UNIQUE.
/ denotes options, but consistency is required in selecting between options across corresponding elements of the queries.''', 

'''Equivalent Queries:
SELECT DISTINCT c1 FROM t1;
SELECT c1 FROM t1;
Schema Conditions:
c1 is UNIQUE.''',

'''Equivalent Queries:
SELECT c1 FROM t1 WHERE c1 INTERSECT SELECT c1 FROM t1 WHERE d2;
SELECT c1 FROM t1 WHERE c1 AND d2;
Schema Conditions:
c1 is UNIQUE.''',

'''Equivalent Queries:
SELECT c1 FROM t1 WHERE c1 UNION SELECT c1 FROM t1 WHERE d2;
SELECT c1 FROM t1 WHERE d1 OR d2;
Schema Conditions:
c1 is UNIQUE.''',

'''Equivalent Queries:
SELECT _ FROM t1 WHERE GROUP BY c1, c2, ...;
SELECT _ FROM t1 WHERE GROUP BY c1;
Schema Conditions:
c1 is UNIQUE.''',

'''Equivalent Queries:
SELECT c1 FROM t1 EXCEPT (q1);
SELECT c1 FROM t1 WHERE c1 NOT IN (q1);
Schema Conditions:
c1 is UNIQUE and NON_NULL.''',

'''Equivalent Queries:
SELECT COUNT(*) FROM t1;
SELECT COUNT(c1) FROM t1;
Schema Conditions:
c1 is NON_NULL.''',

'''Equivalent Queries:
SELECT c1 FROM t1 WHERE c1 IS NOT NULL;
SELECT c1 FROM t1;
Schema Conditions:
c1 is NON_NULL.''',

'''Equivalent Queries:
SELECT MIN/MAX(c1) FROM t1;
SELECT c1 FROM t1 ORDER BY c1 ASC/DESC LIMIT 1;
Schema Conditions:
t1 is not empty.
/ denotes options, but consistency is required in selecting between options across corresponding elements of the queries.''',

'''Equivalent Queries:
SELECT * FROM t1;
SELECT c1, c2, ... FROM t1;
Schema Conditions:
t1 consists of only c1, c2, ...''',

'''Equivalent Queries:
SELECT _ FROM t1 WHERE c1 = 'x';
SELECT _ FROM t1 WHERE c1 = x;
Schema Conditions:
x is a number not starting with zero.''',

'''Equivalent Queries:
SELECT _ FROM t2 WHERE c2 IN (SELECT c1 FROM t1 WHERE d1);
SELECT _ FROM t1 JOIN t2 ON t1.c1 = t2.c2 WHERE d1;
Schema Conditions:
A primary key-foreign key relation, where t1.c1 is the primary key and t2.c2 is the foreign key.''',

'''Equivalent Queries:
SELECT X FROM t1 JOIN t2 ON t1.c1 = t2.c2;
SELECT X FROM t2;
Schema Conditions:
t1.c1 must be non-composite and X can be any column(s) in t2.''',

'''Equivalent Queries:
SELECT c1 FROM t1 AS t;
SELECT c1 FROM t1 t;
Schema Conditions:
None.''',

'''Equivalent Queries:
SELECT _ FROM t1 WHERE c1 IN/NOT IN (x, y, ...);
SELECT _ FROM t1 WHERE c1 =/!= x OR/AND c1 =/!= y OR/AND ...;
Schema Conditions:
/ denotes options, but consistency is required in selecting between options across corresponding elements of the queries.''',

'''Equivalent Queries:
SELECT t1.c1 FROM table1 JOIN t2 ON t1.c1 = t2.c2;
SELECT t2.c2 FROM t1 JOIN t2 ON t1.c1 = t2.c2;
Schema Conditions:
None.''',

'''Equivalent Queries:
SELECT c1 FROM t1 WHERE c1 IN (SELECT c1 FROM t1 WHERE d1);
SELECT c1 FROM t1 WHERE d1;
Schema Conditions:
None.''',

'''Equivalent Queries:
q1;
q1 UNION/INTERSECT q1;
Schema Conditions:
None.''',

'''Equivalent Queries:
SELECT _ FROM t1 WHERE c1 BETWEEN x AND y;
SELECT _ FROM t1 WHERE c1 >= x/y and c1 <= x/y;
Schema Conditions:
/ denotes options, but consistency is required in selecting between options across corresponding elements of the queries.''',

'''Equivalent Queries:
SELECT _ FROM t1 WHERE c1 !=/>/<=>/= x;
SELECT _ FROM t1 WHERE NOT c1 =/=/>/<=>/= x;
Schema Conditions:
/ denotes options, but consistency is required in selecting between options across corresponding elements of the queries.'''
    ]
