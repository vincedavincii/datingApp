import pymysql
from prettytable import PrettyTable

DATABASE_NAME = "dateUs"
TABLE_NAME = "members"


def ensure_database(db):
    with db.cursor() as c:
        c.execute(
            f"CREATE SCHEMA IF NOT EXISTS `{DATABASE_NAME}` DEFAULT CHARACTER SET utf8;"
        )


def ensure_table(db):
    with db.cursor() as c:
        c.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                userid INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
                firstname VARCHAR(50),
                lastname VARCHAR(50),
                sex VARCHAR(10) NOT NULL,
                age INT,
                country_location VARCHAR(50)
            );
            """
        )


def convert_line_to_values(line):
    values = line.strip().split(",")
    return values


def member_check():
    firstname = input("Your name: ")
    if firstname == "":
        raise ValueError("You must provide a first name?")
    sex = input("Your is your Sex - Male, Female:").capitalize()
    if sex not in ("female", "Female", "FEMALE", "male", "Male", "MALE"):
        raise ValueError("provide a valid sex, only Male or Female for this App")
    country_location = input("Your country location: ").capitalize()
    age = int(input("What is your Age: "))
    if age < 15:
        print("You are damn too young, Go read your books!")
        exit(1)
    elif age > 50:
        print("You're too old to use our app, Try facebook!")
        exit(1)
    else:
        return firstname, sex, age, country_location


def older10yrs(db, data):
    with db.cursor() as c:
        c.execute(
            f"SELECT firstname,lastname, sex, age, country_location FROM {TABLE_NAME} "
            f"WHERE age = {int(data[2]) + 10} and sex != '{data[1]}' ORDER BY RAND()  LIMIT 5;")

        table = PrettyTable(['First Name', 'Last Name', 'Sex', 'Age', 'Location'])

        for row in c.fetchmany(5):
            table.add_row(row[:5])
        print(table)

        # for row in c.fetchall():
        #     firstname, sex, age, country_location = row
        #     print(f"{firstname} ({sex}) is {age} old and from {country_location}.")


def country_list(db, data):
    with db.cursor() as c:
        c.execute(f"SELECT DISTINCT country_location FROM `{TABLE_NAME}` ORDER BY country_location")
        print("Here are the countries we have clients:")
        for row in c.fetchall():
            print(row[0], "| ", end="")


def country_based(db, data):
    country = input("Which location would you like matches from?\n")
    with db.cursor() as c:
        c.execute(
            f"SELECT firstname, lastname, sex, age, country_location FROM {TABLE_NAME} "
            f"WHERE country_location = '{country}' and sex != '{data[1]}' ORDER BY RAND();")

        table = PrettyTable(['First Name', 'Last Name', 'Sex', 'Age', 'Location'])

        for row in c.fetchmany(5):
            table.add_row(row[:5])
        print(table)

        # for row in c.fetchall():
        #     firstname, sex, age, country_location = row
        #     print(f"{firstname} ({sex}) is {age} old and from {country_location}.")


if __name__ == "__main__":

    db = pymysql.connect(host='127.0.0.1', user='vincent', password='12345', database="")
    ensure_database(db)
    db.close()

    db = pymysql.connect(host='127.0.0.1', user='vincent', password='12345', database=DATABASE_NAME)
    ensure_table(db)

    sql = f"""
        INSERT INTO {TABLE_NAME}
        (firstname, lastname, sex, age, country_location) VALUES
        (%s, %s, %s, %s, %s)
    """

    db = pymysql.connect(host='127.0.0.1', user='vincent', password='12345', database=DATABASE_NAME)
    file_path = "DatingAppData.csv"
    with db.cursor() as c:
        with open(file_path) as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                values = convert_line_to_values(line)
                c.execute(sql, values)
                if i > 0 and i % 100 == 0:
                    db.commit()
        db.commit()

    choice_functions = {"t": older10yrs, "l": country_list, "c": country_based}
    print(
        f"Welcome to our app, let's get to know you.")
    while True:
        try:
            data = member_check()
            break
        except ValueError as ve:
            print(str(ve))
    while True:
        print(
            f"Choose an option?:\n",
            "t: Show matches 10 years older\n",
            "l: show country listing we have in our App\n",
            "c: Show matches in a specific country\n",
            "q: quit\n",
        )
        choice = input("> ").lower()
        if choice == "q":
            print("Closing app...")
            break
        elif choice in choice_functions:
            choice_functions[choice](db, data)
        else:
            print(f"Unknown choice: '{choice}'. Try again.")
        print("----")
