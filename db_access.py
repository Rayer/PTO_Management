import mysql.connector as sql

class member_access:
    def __init__(self):
        self.conn = sql.connect(user='mcds', password='mcds', database='mcds')

    def employee_info(self, name):
        cursor = self.conn.cursor()
        cursor.execute('select * from mcds_tw_members where name = \'{}\''.format(name))
        result = cursor.fetchone()
        column_names = cursor.column_names
        ret = {}
        for i in range(0, cursor.column_names.__len__()):
            ret.update({column_names[i]: '' if result[i] is None else result[i]})
        cursor.close()
        return ret

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()





