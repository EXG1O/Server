BOT_DEAFAULT_FILES = {
	'User-Commands.json': [
		{
			'Command_Name': 'Вывод статистики',
			'Command': '!Статистика',
			'Command_Answer': """\
Вас зовут: {user}
Ваш балланс: {db[2]}
Ваш уровень: {db[1]}
Ваш опыт: {db[3]}"""
		},
		{
			'Command_Name': 'Вывод статистики другого пользователя',
			'Command': '!Статистика пользователя {take_user_id}',
			'Command_Answer': """\
Имя пользователя: {other_user}
Ранг пользователя: {other_db[4]}
Балланс пользователя: {other_db[2]}
Уровень пользователя: {other_db[1]}
Опыт пользователя: {other_db[3]}"""
		},
		{
			'Command_Name': 'Вывод список команд',
			'Command': '!Список команд',
			'Command_Answer': """\
Список команд:
{all_commands}"""
		}
	],
	'Log.txt': []
}