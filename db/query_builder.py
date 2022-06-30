# -*- coding: utf-8 -*-
from .helpers import bind_field

"""
    Builders to statements that are used for more than one query.
"""
class common:
    def build_where(self, params):
        conditions = ''
        binds = ()

        if not isinstance(params, list):
            raise Exception('WHERE clausule must to receive a list of dicts in \'where\' property.')

        for where in params:
            if not isinstance(where, dict):
                raise Exception('WHERE clausule must to receive a list of dicts in \'where\' property.')

            concat = 'AND'
            col = None
            comparator = None
            comparatorBind = None
            group = None

            if 'concat' in where.keys():
                concat = {
                    'and': 'AND',
                    'or': 'OR'
                }[where['concat']]

            if not 'col' in where.keys() and not 'group' in where.keys():
                raise Exception('WHERE conditions must to have \'col\' or \'group\' properties to be used in query.')


            if len(conditions) > 0:
                conditions += f'{concat} '

            if 'group' in where.keys():
                group = self.build_where(where['group'])

                for bind in group['binds']:
                    binds = binds + (bind,)

                conditions += f"({group['conditions']}) "
            else:
                if 'col' in where.keys():
                    col = bind_field(where['col'])

                if 'equals' in where.keys():
                    comparator = '='
                    comparatorBind = self.get_query_bound(where['equals'])
                    binds = binds + (self.get_query_bind(where['equals']),)
                elif 'not_equals' in where.keys():
                    comparator = '<>'
                    comparatorBind = self.get_query_bound(where['not_equals'])
                    binds = binds + (self.get_query_bind(where['not_equals']),)
                elif 'is' in where.keys():
                    comparator = 'IS NULL'
                    comparatorBind = ''
                elif 'not_is' in where.keys():
                    comparator = 'IS NOT NULL'
                    comparatorBind = ''
                elif 'like' in where.keys():
                    comparator = f"LIKE CONCAT('%%', {self.get_query_bound(where['like'])}, '%%')"
                    binds = binds + (self.get_query_bind(where['like']),)
                    comparatorBind = ''
                elif 'not_like' in where.keys():
                    comparator = f"NOT LIKE CONCAT('%%', {self.get_query_bound(where['not_like'])}, '%%')"
                    binds = binds + (self.get_query_bind(where['not_like']),)
                    comparatorBind = ''
                elif 'in' in where.keys():
                    comparator = 'IN('

                    for value in where['in']:
                        comparator += f'{self.get_query_bound(value)}, '
                        binds = binds + (self.get_query_bind(value),)

                    comparator = comparator[0:-2] + ')'
                    comparatorBind = ''
                elif 'not_in' in where.keys():
                    comparator = 'NOT IN('

                    for value in where['in']:
                        comparator += f'{self.get_query_bound(value)}, '
                        binds = binds + (self.get_query_bind(value),)

                    comparator = comparator[0:-2] + ')'
                    comparatorBind = ''

                conditions += f'{col} {comparator} {comparatorBind} '

        return {
            'conditions': conditions,
            'binds': binds
        }



    def build_limit(self, limit: int) -> str:
        if not isinstance(limit, int):
            raise Exception('Limit must be a integer value')

        return f'LIMIT {limit}'


    def build_take(self, amount: int) -> str:
        if not isinstance(amount, int):
            raise Exception('Offset in \'take\' property must be a integer value')

        return f'OFFSET {amount}'


    def get_query_bound(self, value, error_message = None) -> str:
        bound = None

        if error_message == None:
            error_message = f'Cannot determine type of \'{value}\''

        if isinstance(value, str):
            bound = '%s'
        elif isinstance(value, int):
            bound = '%s'
        elif isinstance(value, float):
            bound ='%s'
        elif value == None:
            bound = 'NULL'

        if bound == None:
            raise Exception(error_message)

        return bound


    def get_query_bind(self, value):
        if value == True:
            value = 1
        elif value == False:
            value = 0

        return value

class select:
    """
        Build SELECT columns/fields list.

        Uses: params.columns, params.custom_fields
    """
    def build_columns(self) -> str:
        query = ''

        if not 'columns' in self.params.keys() and not 'custom_fields' in self.params.keys():
            query += '*, '
        else:
            if 'columns' in self.params.keys():
                for column in self.params['columns']:
                    column = bind_field(column)
                    query += f'{column}, '

            if 'custom_fields' in self.params.keys():
                for alias in self.params['custom_fields']:
                    if isinstance(self.params['custom_fields'][alias], str):
                        query += f"{self.params['custom_fields'][alias]} AS `{alias}`, "
                    elif isinstance(self.params['custom_fields'][alias], dict):
                        query += '(' + self.build_select_query(self.params['custom_fields'][alias]) + f') AS `{alias}`, '
                    else:
                        raise Exception(f"Unknow subquery of type {type(self.params['custom_fields'][alias])} provided in {alias} with value {self.params['custom_fields'][alias]}")

        return query[0:-2]


    """
        Build FROM statements.

        Uses: params.from
    """
    def build_from(self) -> str:
        query = ''

        if isinstance(self.params['from'], str):
            self.params['from'] = [self.params['from']]

        for source in self.params['from']:
            if isinstance(source, str):
                query += bind_field(source) + ', '
            elif isinstance(source, dict):
                if not 'alias' in source.keys():
                    raise Exception('You must provide a alias (in \'alias\' property, as string) to pseudo-sources in SELECT queries.')

                if not 'query' in source.keys():
                    raise Exception('You must provide a query (in \'query\' property, as dict, with select query building structure) to pseudo-sources in SELECT queries.')


                query += '(' + self.build(source['query']) + f") AS `{source['alias']}`, "
            else:
                raise Exception(f'Invalid source {source} in from list. Provide a list with items on type string or dict')

        return query[0:-2]


    """
        Build JOIN statements.

        Uses: params.join
    """
    def build_joins(self) -> str:
        query = ''

        if not isinstance(params['join'], list) or (isinstance(params['join'], list) and len(params['join']) == 0):
            raise Exception('Property \'join\' must be a valid list with at least one dict item')

        for join in params['join']:
            if not isinstance(join, dict):
                raise Exception('Each join item on query must to be a valid dict.')

            direction = 'inner'
            alias = ''
            comparator = '='

            if not 'with' in join.keys():
                raise Exception('String \'with\' property is required in joins')

            if not 'left' in join.keys():
                raise Exception('String \'left\' property is required in joins')

            if not 'right' in join.keys():
                raise Exception('String \'right\' property is required in joins')

            directions = {
                'left': 'LEFT JOIN',
                'right': 'RIGHT JOIN',
                'inner': 'INNER JOIN',
                'outer': 'OUTER JOIN'
            }

            if 'direction' in join.keys():
                direction = join['direction']

            if not direction in directions:
                raise Exception('Unknow left direction \'direction\'. Choose between inner (default), left, right or outer')

            direction = directions[direction]

            new_source = None

            if 'alias' in join.keys():
                alias = ' AS ' + bind_field(join['alias'])

            if isinstance(join['with'], str):
                new_source = bind_field(join['with']) + alias
            elif isinstance(join['with'], dict):
                if not 'alias' in join['with'].keys():
                    raise Exception('You must provide a alias (in \'alias\' property, as string) to pseudo-sources in SELECT queries.')

                if not 'query' in join['with'].keys():
                    raise Exception('You must provide a query (in \'query\' property, as dict, with select query building structure) to pseudo-sources in SELECT queries.')

                new_source = '(' + self.build(join['with']['query']) + f") AS `{join['with']['alias']}`{alias}"

            left = bind_field(join['left'])
            right = bind_field(join['right'])

            if 'comparator' in join.keys():
                comparator = join['comparator']

            query += f'{direction} {new_source} ON {left} {comparator} {right} '

        return query[0:-1]


    """
        Builds GROUP BY statement.

        Uses: params.group
    """
    def build_group(self) -> str:
        query = ''

        if not isinstance(self.params['group'], str) and not isinstance(self.params['group'], list):
            raise Exception('\'group\' property must to be a string or a list of strings')

        if isinstance(self.params['group'], str):
            self.params['group'] = [self.params['group']]

        query += 'GROUP BY '

        for group in self.params['group']:
            query += bind_field(group) + ', '

        return query[0:-2]


    """
        Use the building methods to return the entire query.
    """
    def build(self, params: dict):
        self.params = params
        self.common = common()

        if not 'from' in self.params.keys():
            raise Exception('Property \'from\' is required in SELECT queries.')
        elif not isinstance(self.params['from'], list) and (isinstance(self.params['from'], list) and len(self.params['from']) == 0) and not isinstance(self.params['from'], str):
            raise Exception('Property \'from\' in SELECT queries must to be of type str, list of strings or dict')

        query = 'SELECT ' + self.build_columns() + ' FROM ' + self.build_from() + ' '
        binds = ()

        if 'join' in self.params.keys():
            query += self.build_joins() + ' '

        if 'where' in self.params.keys():
            where = self.common.build_where(self.params['where'])

            binds = where['binds']
            query += f"WHERE {where['conditions']} "

        if 'group' in self.params.keys():
            query += self.build_group() + ' '

        if 'limit' in self.params.keys():
            query += self.common.build_limit(self.params['limit']) + ' '

        if 'take' in self.params.keys():
            query += self.common.build_take(self.params['take']) + ' '

        return {
            'query': query,
            'binds': binds
        }


class insert:
    def build(self, params: dict):
        self.params = params
        self.common = common()

        if not 'in' in self.params.keys():
            raise Exception('Property \'in\' is required in INSERT queries.')
        elif not isinstance(self.params['in'], str):
            raise Exception('Property \'in\' in INSERT queries must to be of type str')

        if not 'data' in self.params.keys():
            raise Exception('Property \'data\' is required in INSERT queries.')
        elif not isinstance(self.params['data'], dict) and not isinstance(self.params['data'], list):
            raise Exception('Property \'data\' in INSERT queries must to be of type dict or a list of dict\'s.')

        query = f"INSERT INTO {bind_field(self.params['in'])} ("

        if isinstance(self.params['data'], dict):
            self.params['data'] = [self.params['data']]

        keys = self.params['data'][0].keys()

        for row in self.params['data']:
            if row.keys() != keys:
                raise Exception('All INSERT queries must to have the same columns specification defined in \'data\' indexes. To use a different column set, please commit with another insert command.')

        for key in keys:
            query += bind_field(key) + ', '

        query = query[0:-2] + ') VALUES '

        binds = ()

        for row in self.params['data']:
            query += '('

            for value in row.values():
                if value == None:
                    continue

                binds = binds + (self.common.get_query_bind(value),)

            for key in row.keys():
                bound = self.common.get_query_bound(row[key], f'Cannot determine the type of value [{row[key]}] to field \'{key}\'.')

                query += f'{bound}, '

            query = query[0:-2] + '), '

        query = query[0:-2]

        return {
            'query': query,
            'binds': binds,
        }


class delete:
    def build(self, params: dict):
        self.params = params
        self.common = common()

        if not 'on' in params.keys() or not isinstance(params['on'], str):
            raise Exception('Property \'on\' is required and needs to be a string referencing a table in database when using DELETE queries.')

        if not 'where' in params.keys():
            raise Exception('Cannot delete without WHERE.')

        where = self.common.build_where(self.params['where'])

        query = f"DELETE FROM {bind_field(self.params['on'])} WHERE {where['conditions']} "

        if 'limit' in self.params.keys():
            query += self.common.build_limit(self.params['limit']) + ' '

        return {
            'query': query,
            'binds': where['binds']
        }


class update:
    def build(self, params: dict):
        self.params = params
        self.common = common()

        if not 'on' in self.params.keys() or not isinstance(params['on'], str):
            raise Exception('Property \'on\' is required and needs to be a string referencing a table in database when using UPDATE queries.')

        if not 'where' in self.params.keys():
            raise Exception('Cannot update without WHERE.')

        if not 'data' in self.params.keys():
            raise Exception('You must to define which fields update to which values in \'data\' dict property.')

        if not isinstance(self.params['data'], dict):
            raise Exception('Property \'data\' in UPDATE queries must to be a dict where each key represents a column, and each value the new column value.')

        where = self.common.build_where(self.params['where'])

        query = f"UPDATE {bind_field(self.params['on'])} SET "
        binds = ()

        for field in self.params['data']:
            binds = binds + (self.common.get_query_bind(self.params['data'][field]),)
            query += f"{bind_field(field)} = %s, "

        query = query[0:-2] + f" WHERE {where['conditions']} "

        if 'limit' in self.params.keys():
            query += self.common.build_limit(self.params['limit']) + ' '

        for bind in where['binds']:
            binds = binds + (bind,)

        return {
            'query': query,
            'binds': binds
        }
