import pandas as pd
import requests

from bs4 import BeautifulSoup
from pandasgui import show

url = 'https://rinkresults.com/list-judges'

page = requests.get(url)

soup = BeautifulSoup(page.text, 'html')

table = soup.find('table')

cells_l = []
officials_l = []
current_country = None

for row in table.find_all('tr'):
    cells = row.find_all('td')
    cells_l.append(cells)

for item in cells_l:
    if len(item) == 2:
        first_col = item[0]
        first_col_text = first_col.get_text(strip=True)


        if first_col.find('img'):
            current_country = first_col_text
        elif current_country:
          officials_l.append([first_col_text, current_country])

for item in cells_l:
    if len(item) == 2:
        second_col = item[1]
        second_col_text = second_col.get_text(strip=True)

        if second_col.find('img'):
            current_country = second_col_text
        elif current_country:
            officials_l.append([second_col_text, current_country])


print(len(officials_l))

officials_l = [i for i in officials_l if len(i[0]) != 0]

print(len(officials_l))

offcial_country = pd.DataFrame(officials_l, columns=['official', 'country'])
show(offcial_country)

offcial_country.to_csv('Offical_Country.csv', index=False)