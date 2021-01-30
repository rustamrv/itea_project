**Stack technology**
1) Python3
2) MongoDB
3) Mongoengine
4) Flask
5) Flask restfull
6) Telebot
7) Google cloud
8) Nginx
9) Gunicorn

**Сущности БД (коллекции)**
1) Продукты
   1. Название
   2. Описание
   3. {Категория}
   4. Цена
   5. Наличие
   6. Картинка
   7. Скидка в процентах
2) Категории
    1. Название
    2. Описание
    3. {parent}
    4. [{subcategory}]
3) Пользователи
    1. telegram id
    2. Номер телефона
    3. Никнейм
4) Корзина 
5) Заказы 
6) Новости
    1. Заголовок
    2. Содержимое
    3. Дата публикации


#Lessons 12
1) Создать абстрактную коллекцию. Она должна содержать два поля created и modified, и хранить в них дату и время. created - время создания объекта,
   modified - время последнего обновления. Логику со временем размещаем в методе save.
   
2) Проинициализировать бот. Описать хендлер /start. 
   При старте приветсвовать пользователя. Создать модуль constants, 
   в котором будем константно хранить текста и другие константы.
   
#Lessons 13
1) Описать хендлер, который будет отрабатывать по клике на кнопку "Новости", Выводить 
   последние 5 новостей отдельными сообщениями
2) Коллекция новостей должна наследовать абстрактную коллекцию (created_at, modified_at, 12.1)
3) Описать хендлер для клика на кнопку определенной категории. Выводить название продуктов, которые
относяться к кликнутой категории. Выводить название продуктов отдельными сообщениями.
   
#Lessons 14
1) Описать метод форматирования продукта (цена с учетом скидки, название, описание, характеритики). Отправлять
   эту информацию под картинкой продукта
2) Описать хендлер для обработки кликов на категории. (Сделано на задание)
3) Описать коллекцию корзину и заказа.

#Lessons 15
1) Реализовать логику для изменения данные профиля (почта, номер телефона, имя, адрес)
Добавить в модель юзер поле адрес. 
   
#lessons 16
1) Нужно создать аккаунт на гугл клоуде. Создать виртуальную машину
   1. 1 ВЦП
   2. 1.7 ГБ ОП
   3. Диск 40 гб
2) Рассылка сообщение (done)
3) Вывод содержимое корзины. При клике корзины выводим с возможности увеличить
или уменьшить количество
4) Оформление заказа. В момент формирования корзины добавить кнопку "Завершить заказ".
После нажатия на кнопку завершить заказ, выводить пользователю всё, что он добавил в корзину.
Запросить у него данные (почта, телефон, адрес)
5) После создание "Новости" в бд, отправлять ее содержимое всем пользователям бота.

#lessons 17
1) Создать REST (в пакете api). REST API должен покрывать следующее модели:
новости, пользователи, заказы (чтение), категории, продукты. Посмотреть в сторонy
blueprint для flask (решить вопрос с созданием с доп. обьекта app).
Использовать flask_restfull 
   

#deploy
1) Установка пакетов:
   1. sudo apt update 
   2. sudo apt install -y mongodb
2) Установка виртуального окружение
   1. python3 -m virtualenv venv
   2. source venv/bin/activate
3) Установка пакетов
   1. pip3 install -r requirements.txt
4) Создать ключи и установить
   1. openssl genrsa -out webhook_pkey.pem 2048
   2. openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem 
      > common name ip - адрес
   4. sudo cp webhook_pkey.pem /etc/ssl/private/
   5. sudo cp webhook_cert.pem /etc/ssl/certs/
5) Nginx
   1. cd /etc/nginx/sites-available/
   2. sudo nano default 
      >listen 80 default_server; <br/>
      listen 443 ssl http2;<br/> 
      ssl_certificate /etc/ssl/certs/webhook_cert.pem; <br/>
      ssl_certificate_key /etc/ssl/private/webhook_pkey.pem; <br/>
      location /bot { <br/>
      proxy_http_version 1.1; <br/>
      proxy_pass http://127.0.0.1:5000/bot; <br/> 
      }<br/> 
      location /api {<br/> 
      proxy_pass http://127.0.0.1:5000/api; <br/>
      proxy_set_header Host $host;<br/>
      proxy_set_header X-Real-IP $remote_addr;<br/>
      }
      >
   3. sudo service nginx restart|stop|start|reload
6) Запуск
   1. gunicorn --bind 127.0.0.1:5000 main_bot:app --daemon
   2. gunicorn --bind 127.0.0.1:5000 app_main:app --daemon 
