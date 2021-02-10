import peewee as pw

database = pw.PostgresqlDatabase('azmoonak', user='postgres', host='127.0.0.1',port=5432,
                        password='1234')