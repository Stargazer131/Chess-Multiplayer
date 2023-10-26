import mysql.connector


class Account:
    def __init__(self, account_id: int, username: str, password: str,
                 win: int, draw: int, lose: int, elo: int):
        self.account_id = account_id
        self.username = username
        self.password = password
        self.win = win
        self.draw = draw
        self.lose = lose
        self.elo = elo

    def __str__(self):
        return f"ID: {self.account_id}, Username: {self.username}, Password: {self.password}" \
               f"Wins: {self.win}, Draws: {self.draw}, Losses: {self.lose}, Elo: {self.elo}"


class AccountDAO:
    def __init__(self, host='localhost', user='root', password='hung2002', database='chess'):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    def get_by_user_and_pass(self, username: str, password: str):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Account WHERE username = %s and password = %s"
        cursor.execute(query, (username, password))
        results = cursor.fetchall()
        if len(results) > 0:
            return self.row_to_object(results[0])

    def get_by_user(self, username: str):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Account WHERE username = %s"
        cursor.execute(query, (username, ))
        results = cursor.fetchall()
        if len(results) > 0:
            return self.row_to_object(results[0])

    def get_by_id(self, account_id: int):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Account WHERE account_id = %s"
        cursor.execute(query, (account_id, ))
        results = cursor.fetchall()
        if len(results) > 0:
            return self.row_to_object(results[0])

    def add(self, username: str, password: str):
        cursor = self.connection.cursor()
        query = "INSERT INTO Account (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        self.connection.commit()

    def update(self, account: Account):
        cursor = self.connection.cursor()
        query = "UPDATE Account " \
                "SET win = %s, draw = %s, lose = %s, elo = %s " \
                "WHERE account_id = %s"

        cursor.execute(query, (
            account.win, account.draw, account.lose, account.elo, account.account_id
        ))
        self.connection.commit()

    @staticmethod
    def row_to_object(parameters: tuple):
        account_id, username, password, win, draw, lose, elo = parameters
        return Account(account_id, username, password, win, draw, lose, elo)

    @staticmethod
    def object_to_row(account: Account):
        return (account.account_id, account.username, account.password,
                account.win, account.draw, account.lose, account.elo)


if __name__ == '__main__':
    pass

