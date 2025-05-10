### Как использовать Makefile

- Создать виртуальное окружение и установить зависимости:

```bash
make install
```

- Запустить основные сервисы Airflow:

```bash
make af-up
```

- Инициализировать базу данных:

```bash
make af-db-init
```

- Обновить базу данных:

```bash
make af-db-upgrade
```

- Создать администратора:

```bash
make af-create-user
```

- Открыть Airflow UI:

```bash
make af-open-ui
```

- Запустить все сервисы (после создания пользователя):

```bash
make start-all
```

- Остановить и удалить контейнеры:

```bash
make down
```

- Для просмотра списка команд:

```bash
make help
```
