# -*- coding: utf-8 -*-
import pymysql
from .helpers import bind_field
from .query_builder import select, insert, delete, update


class DB:
    def __init__(self, config: dict):
        self.config = config
        self.conn = pymysql.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            database=self.config['database'],
            cursorclass=pymysql.cursors.DictCursor
        )

        self.builders = {
            'select': select(),
            'insert': insert(),
            'delete': delete(),
            'update': update(),
        }

        self.last_inserted_id = None

    """
        Run a SELECT query expecting only one result returned.
    """
    def find(self, params: dict):
        query = self.builders['select'].build(params)
        return_data = None

        with self.conn.cursor() as cursor:
            cursor.execute(query['query'], query['binds'])
            data = cursor.fetchone()

            if data:
                return_data = data

        return data


    """
        Run a SELECT query expecting one or more results
    """
    def find_many(self, params: dict):
        query = self.builders['select'].build(params)
        return_data = []

        with self.conn.cursor() as cursor:
            cursor.execute(query['query'], query['binds'])
            data = cursor.fetchall()

            if data:
                return_data = data

        return data


    """
        Use builders to mount queries, and then run and commit it, returning the affected rows by the querie.
    """
    def __commit_and_row_count(self, params, builder: str) -> int:
        query = self.builders[builder].build(params)
        returnData = 0

        with self.conn.cursor() as cursor:
            returnData = cursor.execute(query['query'], query['binds'])
            self.conn.commit()

            if cursor.lastrowid:
                self.last_inserted_id = int(cursor.lastrowid)

        return returnData


    def insert_one(self, params: dict) -> int:
        return self.__commit_and_row_count(params, 'insert')


    def insert_many(self, params: list) -> int:
        return self.__commit_and_row_count(params, 'insert')


    def insert(self, params) -> int:
        if isinstance(params['data'], dict):
            return self.insert_one(params)
        else:
            return self.insert_many(params)


    def delete(self, params: dict) -> int:
        return self.__commit_and_row_count(params, 'delete')


    def update(self, params: dict) -> int:
        return self.__commit_and_row_count(params, 'update')

