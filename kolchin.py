import csv
import re
import os
from prettytable import PrettyTable
from var_dump import var_dump

rus_name_dict = {
    "name": "Название",
    "description": "Описание",
    "key_skills": "Навыки",
    "experience_id": "Опыт работы",
    "premium": "Премиум-вакансия",
    "employer_name": "Компания",
    "Оклад": "Оклад",
    "area_name": "Название региона",
    "published_at": "Дата публикации вакансии"
}


class DataSet:
    def __init__(self, file_name, vacancies_objects):
        self.file_name = file_name
        self.vacancies_objects = vacancies_objects


class Vacancy:
    def __init__(self, name, description, key_skills, experience_id, premium, employer_name, salary, area_name, published_at):
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at


class Salary:
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency


def create_dict_list(content_input, header_input):
    temp_list = []
    for value in content_input:
        dictionary = create_dictionary(value, header_input)
        temp_list.append(dictionary)
    return temp_list


def create_dictionary(value_input, header_input):
    index = 0
    dictionary = {}
    for value in value_input:
        if '\n' in value:
            value_input[index] = ', '.join(value.split('\n'))
        pair = {header_input[index]: re.sub('<.*?>', '', value_input[index])}
        dictionary.update(pair)
        index += 1
        if index == len(header_input):
            index = 0
    global vacancies
    salary = Salary(dictionary['salary_from'], dictionary['salary_to'], dictionary['salary_gross'], dictionary['salary_currency'])
    vacancies.append(Vacancy(dictionary['name'], ' '.join(dictionary['description'].split()), dictionary['key_skills'].split(', '), dictionary['experience_id'], dictionary['premium'], dictionary['employer_name'], salary, dictionary['area_name'], dictionary['published_at']))
    return dictionary


def parse_bool(input_str):
    if input_str == 'True':
        return 'Да'
    if input_str == 'False':
        return 'Нет'


def get_correct_skills(input_skills):
    skills = input_skills.split(',')
    new_skills = []
    for skill in skills:
        new_skills.append(skill.strip())
    return '\n'.join(new_skills)


def create_table_row(inout_row, input_key):
    inout_row[input_key] = ' '.join(inout_row[input_key].split())
    if input_key == 'premium':
        inout_row[input_key] = parse_bool(inout_row[input_key])
    if input_key == 'key_skills':
        inout_row[input_key] = get_correct_skills(inout_row[input_key])
    if len(inout_row[input_key]) > 100:
        inout_row[input_key] = inout_row[input_key][0:100] + "..."

    return inout_row[input_key]


def configurate_table(pretty_table):
    pretty_table.add_autoindex('№')
    pretty_table.align = 'l'
    pretty_table.max_width = 20
    pretty_table.hrules = 1


def create_fields(headers_input, table_head):
    new_fields = ['№']
    if len(headers_input) == 0:
        for head in table_head:
            new_fields.append(head)
    else:
        for head in headers_input:
            new_fields.append(head)
    return new_fields


def print_vacancies(data_vacancies, dic_naming, start_input, end_input, headers_input, filters_input):
    table_head = [dic_naming[x] for x in dic_naming.keys()]
    fields_to_print = create_fields(headers_input, table_head)
    pretty_table = PrettyTable(table_head)
    configurate_table(pretty_table)
    position = 1
    for vacancy in data_vacancies:
        is_next = False
        vacancy_row = [position]
        new_row = formatter(vacancy)
        if len(filters_input) == 2:

            if filters_input[0] == 'Идентификатор валюты оклада':
                salary = new_row['Оклад']
                if filters_input[1] not in salary:
                    continue
            # попытки сделать 4.2
            if filters_input[0] == 'Оклад' and (int(filters_input[1]) < int(vacancy['salary_from'].split('.')[0]) or int(filters_input[1]) > int(vacancy['salary_to'].split('.')[0])):
                continue
            if filters_input[0] == 'Название' and filters_input[1] != new_row['name']:
                continue
            if filters_input[0] == 'Компания' and filters_input[1] != new_row['employer_name']:
                continue
            if filters_input[0] == 'Описание' and filters_input[1] != new_row['description']:
                continue
            if filters_input[0] == 'Премиум-вакансия' and filters_input[1] != parse_bool(new_row['premium']):
                continue
            if filters_input[0] == 'Навыки':
                count = 0
                for filter_name in filters_input[1].split(', '):
                    if filter_name not in new_row['key_skills']:
                        continue
                    count += 1
                if count != len(filters_input[1].split(', ')):
                    continue
            if filters_input[0] != 'Оклад' and filters_input[0] != 'Название' and filters_input[0] != 'Компания' and filters_input[0] != 'Описание' and filters_input[0] != 'Премиум-вакансия' and filters_input[0] != 'Навыки':
                for en_name in dic_naming.keys():
                    if dic_naming[en_name] == filters_input[0]:
                        if filters_input[1] not in new_row[en_name]:
                            is_next = True
                            break
            if is_next:
                continue
        for key in new_row.keys():
            refactor_row = create_table_row(new_row, key)
            vacancy_row.append(refactor_row)
        position += 1
        pretty_table.add_row(vacancy_row)
    if position == 1:
        print('Ничего не найдено таблицу не печатать')
    else:
        print(pretty_table.get_string(fields=fields_to_print,
                                      start=start_input - 1 if start_input != 0 else 0,
                                      end=end_input - 1 if end_input != len(data_vacancies) else len(data_vacancies)))


def csv_reader(file_name):
    content = []
    with open(file_name, encoding='utf-8-sig', mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader)
        for row in reader:
            if '' in row or len(row) != len(header):
                continue
            else:
                content.append(row)
        return [header, content]


def csv_filer(reader, list_naming):
    return create_dict_list(list_naming, reader)


def formatter(row):
    experience = {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет"
    }
    currency = {
        "AZN": "Манаты",
        "BYR": "Белорусские рубли",
        "EUR": "Евро",
        "GEL": "Грузинский лари",
        "KGS": "Киргизский сом",
        "KZT": "Тенге",
        "RUR": "Рубли",
        "UAH": "Гривны",
        "USD": "Доллары",
        "UZS": "Узбекский сум"
    }
    formatted_row = {}
    for key in row.keys():
        if key == 'experience_id':
            pair = {key: experience[row[key]]}
            formatted_row.update(pair)
        elif key == 'salary_from':
            if row['salary_gross'] == 'True':
                gross = 'Без вычета налогов'
            else:
                gross = 'С вычетом налогов'
            num1 = get_partial_num(row[key].split('.')[0])
            num2 = get_partial_num(row['salary_to'].split('.')[0])
            pair = {"Оклад": f"{num1[0]} {num1[1]} - {num2[0]} {num2[1]} "
                             f"({currency[row['salary_currency']]}) ({gross})"}
            formatted_row.update(pair)
        elif key == 'salary_to' or key == 'salary_currency' or key == 'salary_gross':
            continue
        elif key == 'published_at':
            date = str(row[key]).replace('T', '-').split('-')
            pair = {key: f"{date[2]}.{date[1]}.{date[0]}"}
            formatted_row.update(pair)
        else:
            pair = {key: row[key]}
            formatted_row.update(pair)

    return formatted_row


def get_partial_num(num):
    second_part = num[-3:]
    first_part = num.replace(second_part, '')
    return [first_part, second_part]


def is_input_correct(filtesr):
    if len(filtesr) == 1:
        print('Формат ввода некорректен таблицу не печатать')
        exit()
    if len(filtesr) == 2 and filtesr[0] not in rus_name_dict.values() and filtesr[0] != 'Идентификатор валюты оклада' :
        print('Параметр поиска некорректен таблицу не печатать')
        exit()


def is_empty_file(file):
    if os.stat(file).st_size == 0:
        print('Пустой файл')
        exit()


vacancies = []
file = input('Введите название файла: ')
filters = input('Введите параметр фильтрации: ').split(': ')
filters = list(filter(None, filters))
is_input_correct(filters)
sorting = input('Введите параметр сортировки: ')
is_reverse = input('Обратный порядок сортировки (Да / Нет): ')
is_input_correct(filters)
vacancies_to_print = input('Введите диапазон вывода: ').split()
headers_to_print = input('Введите требуемые столбцы: ').split(', ')
headers_to_print = list(filter(None, headers_to_print))
is_empty_file(file)
reader_result = csv_reader(file)
headers = reader_result[0]
contents = reader_result[1]
if len(contents) == 0:
    var_dump(DataSet(file, vacancies))
    exit()
dictionaries = csv_filer(headers, contents)
is_input_correct(filters)
var_dump(DataSet(file, vacancies))