import mechanicalsoup
import pandas as pd
import sqlite3

# scrape.py:
# Download the URL
# Parse the table entries into arrays
# Create a DataFrame
# Load into SQLite


# Download the URL #
url = "https://en.wikipedia.org/wiki/List_of_cat_breeds"
browser = mechanicalsoup.StatefulBrowser()
browser.open(url)


# Parse the table entries into arrays #
tables = browser.page.find("table")
#print(tables)
#exit()
#tbody = tables.find("tbody")
th = tables.find_all("th")
td = tables.find_all("td")
columns = [value.text.replace("\n", "") for value in td]
titles = [value.text.replace("\n", "") for value in th]

titles = titles[7:]
#print(titles)
#exit()

#distribution = [value.text.replace("\n", "") for value in th]
#distribution = distribution[:98]
# print(distribution)


# print(columns)


#columns = columns[6:1084]
#print(columns)

# Create a DataFrame #
column_names = ["Breed",
                "Origin",
                "Type",
                "Body Type", 
                "Fur Type"]

# column[0:][::11]
# column[1:][::11]
# column[2:][::11]

dictionary = {"Title": titles}

for idx, key in enumerate(column_names):
    dictionary[key] = columns[idx:][::6]

df = pd.DataFrame(data = dictionary)
#print(df.head())
#print(df.tail())


# Load into SQLite #
connection = sqlite3.connect("cats.db")
cursor = connection.cursor()
cursor.execute("create table cats (title, " + ",".join(column_names) + ")")
for i in range(len(df)):
    cursor.execute("insert into cats values (?,?,?,?,?,?)", df.iloc[i])

connection.commit()

connection.close() 