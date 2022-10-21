# version 1.4 
# Импортируем  необходимые библиотеки

# Библиотека для получения сведений о сетевых интерфейсах
import ifaddr
# Библиотека для подключения к портам
import socket
# Библиотека для работы с файлами
import os
# Библиотека для работы с датой и временем
import datetime
# Модуль для работы с процессами и выводами
from subprocess import PIPE, Popen
# Модуль для оформления вывода в виде таблиц
from tabulate import tabulate

# Переменная для хранения текущей даты
now = datetime.datetime.now()


def fn_ipaddresses():
    '''
    Функция fn_ipaddresses возвращает информацию о параметрах сетевых интерфейсов локального хоста
        Функция не имеет никаких аргументов
        Функция  возвращает словарь следующего вида: (IP-address, Net-prefix) для всех интерфейсов узла, на котором запускается код.
    Пример:   {'ipv4': [('169.254.214.47', 16), ('10.177.13.64', 22), ('169.254.106.101', 16), ('169.254.228.140', 16), ('127.0.0.1', 8)], 
               'ipv6': [('fe80::94b5:13b2:7e43:d62f', 0), ('fe80::bdf6:fbc9:a2c:6a65', 0), ('::1', 0)]}
    '''
    
    print(f"\nШАГ 1 СКАНИРОВАНИЕ СЕТЕВЫХ ИНТЕРФЕЙСОВ:")
    # Создаем словарь для хранения полученных значений
    ip_list ={'ipv4':[], 'ipv6':[]}
    # Находим самое длинное наименование сетевого интерфейса (считаем кол-во символов в названии + 1)
    max_len = max([len(adapter.nice_name) for adapter in ifaddr.get_adapters()]) + 1

    # В цикле перебираем все полученые значения с помощью ifaddr.get_adapters()
    for adapter in ifaddr.get_adapters():
        print(f"Сетевой интерфейс:  {adapter.nice_name.ljust(max_len,' ')} [просканирован]")
        # В цикле из множества полученых значений достаем ip 
        for ip in adapter.ips:
            # Преобразуем полученное значения для дальнейшей работы
            ip.ip = ((''.join(str(ip.ip))).split("'"))
            # В условии проверяем текущий элемент на наличие '(', в адресах типа Ipv6 присутствует этот символ вначале, тем самым отбираем их для записи в словарь
            if ip.ip[0] == '(':
                # Соединяем ip и prefix в кортеж, для последующей записи в словарь
                tuple = (ip.ip[1],ip.network_prefix)
                # Полученный кортеж записываем в словарь
                ip_list['ipv6'].append(tuple)
            # При невыполнении условия (получаем ipv4)
            else:
                tuple = (ip.ip[0],ip.network_prefix)
                ip_list['ipv4'].append(tuple)
    
    print(f"\nВЫВОД:")
    # С помощью tabulate выводим полученный слоаврь в табличном виде
    print(tabulate(ip_list, headers='keys', tablefmt='psql', stralign='left'))
    return(ip_list)


def fn_portscan(**ip):
    '''
    Функция fn_portscan, проверяет доступность портов.
        Функция ожидает в качестве аргумента словарь IP-адресов (например, сформированный ф-цией fn_ipaddresses)
        Функция формирует 2 файла: файл с открытыми портами, файл с закрытыми портами. Каждый файл содержит набор строк вида: 
            [19-10-2022 23:18] [169.254.214.47] Port OPEN: 5, 6, 7, 8,
            [19-10-2022 23:18] [169.254.214.47] Port CLOSE: 1, 2, 3, 4,
    '''
    
    # Проверка, преданы ли в ф-цию аргументы
    # Условие: fn_portscan вызвали без аргументов
    if ip == {}:
        # При выполнении условия выводим сообщение об ошибке с описанием ф-ции
        print(f"ОШИБКА, функцияция fn_portscan не выполнена")
        print(fn_portscan.__doc__)
   
    # Условие не выполнено, в ф-цию были переданы аргументы
    else:
        print(f"\nШАГ 2 СКАНИРОВАНИЕ ПОРТОВ:")
        # Объявляем словарь для хранения информации о файлах в которые будем записовать порты (расположение файла, имена файлов, количество строк)
        dict_files = {'file_path':[os.getcwd()], 'file_name':['port_open.txt', 'port_close.txt'], 'string_num':[0, 0]}
        # Кол-во портов которые будут првоеряться 
        ports = 200

        # Контекстный менеджер на открытие двух файлов (создаем их заново)
        with open("port_open.txt",  "w+", encoding="utf-8") as port_open, open("port_close.txt", "w+", encoding="utf-8") as port_close:
            # В цикле проходим по значением из словаря с ip-адресами (полученный в ф-ции fn_ipaddresses)
            for ip_value in ip.values():
                # Спускаемся на еще один вложенный уровень, чтобы достать необходимые нам элементы
                for value in ip_value:
                    # Объявляем строки, которые будем записывать в файлы с портами '[18-10-2022 18:54] [192.168.56.1] Port CLOSE:'
                    str_port_open  = f'\n[{now.strftime("%d-%m-%Y %H:%M")}] [{value[0]}] Port OPEN: '
                    str_port_close = f'\n[{now.strftime("%d-%m-%Y %H:%M")}] [{value[0]}] Port CLOSE: '
                    # В цикле получаем на вход ip и подключаемся последовательно к портам с 1 по port
                    for port in range(1, (ports + 1)):
                        # Расчитываем процент текущего порта из общего кол-ва портов
                        percent = (port/ports) * 100
                        # Объявляем стркоу для хранения записи  и последующего ее вывода
                        st = f"Сканирование ip: {(value[0]).ljust(len((max(ip.values())[0])[0]) + 1)} [порт {port} / {ports}]" + f" {str(round(percent))} %"
                        # Выводим запись вида: 'Сканирование ip: fe80::bdf6:fbc9:a2c:6a65   [порт 100 / 100] 100 %'
                        print('\r', st, sep='', end='', flush=True)
                        # Работаем с сокетом
                        sockt = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                        # Время соединения
                        sockt.settimeout(0.01)
                        # Обрабатываем исключения
                        try: 
                            # При положительном соединении
                            connect = sockt.connect((value[0],port)) 
                            # Добавляем запись с текущем портом в строку, которую будем записывать в файл с портами
                            str_port_open += str(port) + ', '
                            # Закрываем содинение
                            connect.close() 
                        except: 
                            # При отрицательном соединении
                            # Добавляем запись с текущем портом в строку, которую будем записывать в файл с портами
                            str_port_close += str(port) + ', '

                    # Условие: есть запись о портах в строке (файл port_open.txt)
                    if len(str_port_open) > len(f'\n[{now.strftime("%d-%m-%Y %H:%M")}] [{value[0]}] Port OPEN: '):
                        # Делаем запись строки (спортами) в файл
                        # [:-2] срез, чтобы в документ при записи не попал последний символ строки этот символ - ','
                        port_open.write (str_port_open [:-2])
                        # Доабвляем единицу к количеству строк в файле и записываем это значение в словарь (будем выводить информацию о строках внутри файла в конце)
                        dict_files['string_num'][0] += 1

                    # Условие: есть запись о портах в строке (файл port_close.txt)    
                    if len(str_port_close) > len(f'\n[{now.strftime("%d-%m-%Y %H:%M")}] [{value[0]}] Port CLOSE: '):
                        # Делаем запись строки (спортами) в файл
                        # [:-2] срез, чтобы в документ при записи не попал последний символ строки этот символ - ','
                        port_close.write(str_port_close[:-2])
                        # Доабвляем единицу к количеству строк в файле и записываем это значение в словарь (будем выводить информацию о строках внутри файла в конце)
                        dict_files['string_num'][1] += 1  

                    # Отступ с новой строки после каждого вывода "Сканирование ip: 192.168.56.1               [порт 500 / 500] 100 %"
                    print('')

            print(f"\nВЫВОД:")
            # С помощью tabulate выводим словарь с информацией о файлах в которые записывали открытые и закрытые порты
            print(tabulate(dict_files, headers=['Раположение файла', 'Имя файла', 'Строк в файле'], tablefmt='psql', stralign='left'))         


def fn_ipaccess(**ip):
    '''
    Функция fn_ipaccess, проверяет доступность IP-адресов 
    Функция ожидает в качестве аргумента словарь IP-адресов (например, сформированный ф-цией fn_ipaddresses) 
    Функция возвращает кортеж с двумя списками: 
        список доступных IP-адресов;
        список недоступных IP-адресов.
    Пример (возврата): (['192.168.56.1', '169.254.214.47', '10.177.13.64'], ['169.254.106.101'])
    '''
    
    # Проверка, преданы ли в ф-цию аргументы
    # Условие: fn_ipaccess вызвали без аргументов
    if ip == {}:
        # При выполнении условия выводим сообщение об ошибке с описанием ф-ции
        print(f"ОШИБКА, функцияция fn_ipaccess не выполнена")
        print(fn_ipaccess.__doc__)
   
    # Условие не выполнено, в ф-цию были переданы аргументы
    else:
        print(f"\nШАГ 3 ПРОВЕРКА ДОСТУПНОСТИ IP:")
        # Объявляем список для доступных адресов
        ip_access = []
        # Объявляем список для не доуступных адресов
        ip_dont_access = []
        
        # В цикле проходим по значением из словаря с ip-адресами (полученный в ф-ции fn_ipaddresses)
        for ip_value in ip.values():
            # Спускаемся на еще один вложенный уровень, чтобы достать необходимые нам элементы 
            for value in ip_value:
                # Объявляем строку для хранения откредактированного ip-адреса (для последующего вывода на экран) 
                str_log = (value[0]).ljust(len((max(ip.values())[0])[0]) + 1)
                # С помощью библиотеки subprocess выполняем команду: ping -n 1 ip_address
                res = Popen(f"ping -n 1 {value[0]}", shell=True, stdout=PIPE)
                # Записываем в переменную полученный результат выполнения команды ping
                out = str(res.communicate()[0].decode("CP866"))

                # Усдловие: в полученном результате есть фраза - "0% потерь"
                if out.find("0% потерь") > 0:
                    # При выполнении условия доавбляем в список доступных текущий ip-адресс
                    ip_access.append(value[0])
                else:
                    # При НЕ выполнении условия доавбляем в список не доуступных текущий ip-адресс
                    ip_dont_access.append(value[0])

                # Каждую итерацию цикла выводим ip-адресс который сейчас проверяется, пример: "Доступность ip: 192.168.56.1 [проверено]"
                print(f"Доступность ip: {str_log} [проверено]")

        # Обявляем кортеж в который записываем два списка ([доступные ip-адреса], [не доступные ip-адреса])
        ip_aviable = (ip_access, ip_dont_access)
        # Преобразовываем списки [доступные ip-адреса], [не доступные ip-адреса] в словарь, необходимо для вывода в виде таблицы с помощью tabulate
        dict_show_ip_aviable = {'Доступные':ip_aviable[0], 'Не доступные':ip_aviable[1]}
        
        print(f"\nВЫВОД:")
        # Полученный словарь выводим в виде таблицы с помощью tabulate
        print(tabulate((dict_show_ip_aviable), headers='keys', tablefmt='psql'))
        return(ip_aviable)


def main():
    '''
    Функция main немоходима для вызова остальных ф-ций модуля:
        fn_ipaddresses();
        fn_portscan();
        fn_ipaccess().
    Код функции выполняется только при условии, что модуль запускается непосредственно. 
    В случае импорта данного модуля в другие модули код данной функции не выполняется.
    '''

    # Вызываем ф-цию для сканирования сетевых интерфейсов, возвращенный словарь записываем в ip_list
    ip_list = fn_ipaddresses()

    # Вызываем ф-цию для проверки открытых/закрытых портов, отправляем в виде аргумента список ip-адресов полученный ф-цией fn_ipaddresses()
    fn_portscan(**ip_list)

    # Вызываем ф-цию для проверки доступности ip-адресов полученных с помощью ф-ции fn_ipaddresses(), результат записываем в ip_aviable
    ip_aviable = fn_ipaccess(**ip_list)

# Условие: файл запускается самостоятельно (а не импортирован в виде модуля)
if __name__ =="__main__":
    # При выполненнии условия заупскаем основную ф-цию main() 
    main()
