'''
Импортируем основной модуль zachet.py. 
Запускаем функцию fn_ipaddresses и выводим в консоль результат ее выполнения. 
Убеждаемся, что код функции main из модуля zachet.py не выполняется.
'''

import zachet

print('В файл импортирован модуль "zachet.py"\n')
print('В модуле "zachet.py" присутствуют функции:')
# Объявляем список в который помещаем функции задействованные в модуле zachet.py 
# (там много ф-ций, так как мы подключали сторонние библиотеки, но мы их фильтруем по условию: присутствия в наименовании 'fn_')
fn_zachet = [value for value in dir(zachet) if str(value).count('fn_') >= 1]
# Выводим список ф-ций
print(', '.join(fn_zachet))

print(f'\nЗапускаем ф-цию {fn_zachet[1]}')
# Запускаем ф-цию fn_ipaddresses
list_ip = zachet.fn_ipaddresses()

# zachet.fn_portscan()
# zachet.fn_ipaccess()




