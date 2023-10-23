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
    def __init__(self, host='localhost', user='root', password='hayasaka131', database='chess'):
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

    def get_by_id(self, account_id: int):
        cursor = self.connection.cursor()
        query = "SELECT * FROM Account WHERE account_id = %s"
        cursor.execute(query, (account_id, ))
        results = cursor.fetchall()
        if len(results) > 0:
            return self.row_to_object(results[0])

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

    # for row in results:
    #     account_id, username, password, win, draw, lose, elo = row
    #     print(f"Account ID: {account_id}, Username: {username}, Password: {password}, "
    #           f"Wins: {win}, Draws: {draw}, Losses: {lose}, Elo: {elo}")

    # # Insert data into the table
    # insert_query = "INSERT INTO Account (username, password) VALUES (%s, %s)"
    # values = ("NewUser", "Password123")
    # cursor.execute(insert_query, values)
    #
    # # Commit changes to the database
    # connection.commit()


if __name__ == '__main__':
    def calculate_elo(winner_elo, loser_elo, k=32):
        # 1 = 1 win, 0 = 2 win
        # Calculate the expected result for each player
        expected1 = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
        expected2 = 1 - expected1

        result = 1
        # Update Elo ratings for both players
        new_winner_elo = winner_elo + k * (result - expected1)
        new_loser_elo = loser_elo + k * ((1 - result) - expected2)

        return round(new_winner_elo), round(new_loser_elo)


    # Example usage:
    player1_elo = 1600
    player2_elo = 1500

    new_elo1, new_elo2 = calculate_elo(player2_elo, player1_elo)
    print("Player 1's new Elo:", new_elo1)
    print("Player 2's new Elo:", new_elo2)

