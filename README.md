# YaTube
## Социальная сеть для ведения личного блога.
Вы можете делится моментами из своей жизни со своими друзьями, пользователями YaTube, подписываться на понравившихся блогеров,
оставлять комментарии.
![](https://i.ibb.co/4tp3hdJ/image.png)
## Технологии
- [Django](https://github.com/django/django) - фреймворк, который включает в себя все необходимое для быстрой разработки
  различных веб-сервисов

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/s1ntecs/hw05_final.git
```
Перейти в репозиторий:
```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
