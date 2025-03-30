import pandas as pd
import requests
import os
import re

from bs4 import BeautifulSoup
from pandasgui import show

seasons = ['season2425', 'season2324', 'season2223', 'season2122']
competitions = ['fc2025', 'fc2024', 'fc2023', 'fc2022', 'fc2021',
                'ec2025', 'ec2024', 'ec2023', 'ec2022', 'ec2021',
                'wc2025', 'wc2024', 'wc2023', 'wc2022', 'wc2021',
                'gpusa2024', 'gpusa2023', 'gpusa2022', 'gpusa2021',
                'gpcan2024', 'gpcan2023', 'gpcan2022', 'gpcan2021',
                'gpfra2024', 'gpfra2023', 'gpfra2022', 'gpfra2021',
                'gpjpn2024', 'gpjpn2023', 'gpjpn2022', 'gpjpn2021',
                'gpfin2024', 'gpfin2023', 'gpfin2022', 'gpfin2021',
                'gpchn2024', 'gpchn2023', 'gpchn2022', 'gpchn2021',
                'gpf2024', 'gpf2023', 'gpf2022', 'gpf2021',
                'gprus2021', 'gpita2021']
segments = ['SEG001', 'SEG002', 'SEG003', 'SEG004']
segments_japan = ['data0130', 'data0150', 'data0230', 'data0250']

def process_url(season, com, seg, seg_jpn):
  if com in ['wc2023', 'gpjpn2023', 'gpjpn2022', 'gpjpn2021']:
      url = f'https://results.isu.org/results/{season}/{com}/{seg_jpn}.htm'
  else:
      url = f'https://results.isu.org/results/{season}/{com}/{seg}OF.htm'
  return url

def get_judges_panel(url):

  headers = {'User-Agent': 'Mozilla/5.0'}
  response = requests.get(url, headers=headers)

  competition_part = os.path.join(os.path.basename(os.path.dirname(url)), os.path.basename(url))
  competition_name = competition_part.replace('.htm', '')

  judges = []

  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html')

    judge_rows = soup.find_all('tr', class_= ['Line1Blue', 'Line2Blue',
                                              'Line1Red', 'Line2Red',
                                              'Blue0', 'Blue1',
                                              'Red0', 'Red1'])

    for row in judge_rows:
      cells = row.find_all('td')
      if len(cells) > 1:
        role = cells[0].get_text(strip=True)

        if 'Judge' in role:
          judge_name = cells[1].get_text(strip=True)
          judges.append([competition_name, role, judge_name])

  return judges

urls = []
judges_panels_list = []
count = 0

for season in seasons:
  for com in competitions:
    if com in ['wc2023', 'gpjpn2024', 'gpjpn2023', 'gpjpn2022', 'gpjpn2021']:
      for seg_jpn in segments_japan:  
        urls.append(process_url(season, com, None, seg_jpn))
    else:
      for seg in segments:  
          urls.append(process_url(season, com, seg, None))

for url in urls:
  judges = get_judges_panel(url)
  print(judges)

  if judges:
    judges_panels_list.append(judges)
    count += 1

#print(count)

for panel in judges_panels_list:
  for judge in panel:
    judge[0] = judge[0].replace('\\', '')
    judge[2] = re.sub(r'\b(Ms\.|Mr\.)\s*', '', judge[2]).strip()
    if 'jpn' in judge[0] or 'wc2023' in judge[0]:
      judge[2] = " ".join(judge[2].replace('\xa0', ' ').split('\\'))

flat_data = [judge for panel in judges_panels_list for judge in panel]

judge_panel = pd.DataFrame(flat_data, columns=['competition', 'role', 'judge'])
show(judge_panel)

judge_panel.to_csv('csv files/Judge_Panel.csv', index=False)