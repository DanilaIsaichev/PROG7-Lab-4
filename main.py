from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup

import json
from datetime import datetime
from pytz import timezone

def parce_html(file_name = 'data'):
  base_url = 'https://ru.hspu.org'
  print("Starting...")
  print("Time is:", datetime.now(timezone('Europe/Moscow')).time().strftime('%H:%M:%S'))

  url_of_institutes = base_url + '/about/struct-uni/inst/'
  html_of_institutes = urlopen(url_of_institutes)
  bs_of_institutes = BeautifulSoup(BeautifulSoup(html_of_institutes, 'html.parser').prettify(), 'html.parser')

  # Получаем тэги институтов
  tags_of_institutes = bs_of_institutes.find_all('a', {'class': 'btn-inst-list'})

  # Институты
  institutes = []
  # Названия институтов
  names_of_institutes = []
  # Адреса страниц институтов
  urls_of_institutes = []

  # Обрабатываем тэги страницы с институтами
  for tag_of_institute in tags_of_institutes:

    # Считываем ссылку на страницу института
    href_of_institute = tag_of_institute['href'].strip()

    # Считываем название института
    name_of_institute = tag_of_institute.div.get_text().strip()
    names_of_institutes.append(name_of_institute)

    # Кафедры
    departments = []
    # Названия кафедр
    names_of_departments = []
    # Адреса страниц кафедр
    urls_of_departments = []

    if href_of_institute[len(href_of_institute) - 1] != '/':
      url_of_departments = base_url + href_of_institute + '/kafedry/'
    else:
      url_of_departments = base_url + href_of_institute + 'kafedry/'

    # Отлов ошибки, связанной с опечаткой на сайте...
    try:
      html_of_departments = urlopen(url_of_departments)
    except urllib.error.HTTPError:
      if href_of_institute[len(href_of_institute) - 1] != '/':
        url_of_departments = base_url + href_of_institute + '/kafedrf/'
      else:
        url_of_departments = base_url + href_of_institute + 'kafedrf/'
      html_of_departments = urlopen(url_of_departments)

    urls_of_institutes.append(url_of_departments[:len(url_of_departments) - 8])

    bs_of_departments = BeautifulSoup(BeautifulSoup(html_of_departments, 'html.parser').prettify(), 'html.parser')

    tags_of_departments = bs_of_departments.find_all('a', {'class': 'btn-section'})

    # Обрабатываем тэги страницы с кафедрами
    for tag_of_department in tags_of_departments:

      # Считываем название кафедры
      name_of_department = tag_of_department.get_text().strip()

      # Проверяем название кафедры
      if name_of_department[:7] == 'Кафедра':
        names_of_departments.append(name_of_department)

        # Считываем адрес страницы кафедры
        href_of_department = tag_of_department['href'].strip()

        url_of_department = base_url + href_of_department
        urls_of_departments.append(url_of_department)

        html_of_department = urlopen(url_of_department)

        bs_of_department = BeautifulSoup(BeautifulSoup(html_of_department, 'html.parser').prettify(), 'html.parser')

        head_card = bs_of_department.find('div', {'class': 'body-cont-card'}).div.div

        # Обрабатываем тэги страницы заведующего кафедрой, получаем ФИО
        head_of_department_name = head_card.p.a.get_text().strip()

        # Получаем email
        email = head_card.find('i', {'class': 'far fa-envelope'})

        # Проверяем, был ли на странице email
        if email != None:
          email = email.parent.parent.a['href'][7:]
          departments.append({"dep_name": name_of_department, "head_name": head_of_department_name, "email": email})
        else:
          departments.append({"dep_name": name_of_department, "head_name": head_of_department_name})
  
    institutes.append({"institute_name": name_of_institute, "url": url_of_departments[:len(url_of_departments) - 8], "dep_list": departments})

  with open(file_name + '.json', 'w', encoding='utf-8') as file:
      json.dump(institutes, file, ensure_ascii=False, indent=4)

  print("Done. Check " + file_name + ".json")
  print("Time is:", datetime.now(timezone('Europe/Moscow')).time().strftime('%H:%M:%S'))


if __name__ == "__main__":
  parce_html()