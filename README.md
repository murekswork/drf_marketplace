# Описание проекта

Основная идея проекта заключается в реализации сервиса, позволяющего любому, даже самому маленькому магазину предоставить возможность
в несколько кликов создать сервис доставки,а так же любому желающему человеку, в любой момент стать курьером у ближайших 
магазинов. Магазину будет доступна удобная система массовой загрузки товаров и продвинутая система отчетов по продажам.

Реализуется система моментальной регистрации курьеров, всё что нужно - зайти в телеграм бота, отправить трансляцию местоположения,
и получить ближайший заказ.(Продумывается система защиты от недобросовестных курьеров)

Для клиентов доставки создаётся система трекинга заказов, которая показывает актуальное состояние заказа в real-time и позволяет рассчитывать 
время, через которое заказ прибудет, а так же отслеживать местоположение курьера.



## Функционал

На данный момент, в проекте реализован следующий функционал:
- CRUD-функционал для работы с основными сущностями
- Сервис валидации загружаемых данных
- Гибкая система permission-ов
- Поиск товаров
- Система скидок, заказов и отзывов
- Ведется разработка системы периодических отчетов по продажам для магазинов
- Создано курьерское приложения на базе телеграм бота.
- Реализована регистрация курьеров и система трекинга их действий
- Синхронизация состояния заказа между курьерским сервисом и базой данных
- Уведомления об опозданиях по доставке для курьеров

## Сущности

### Магазин

Для управления магазином реализована логика управления permission-ами. Владелец магазина может создавать менеджеров, которых можно наделять различными правами.
#### TODO: Реализовать систему для слежения об актуальных заказах для магазина.

### Продукт

Реализована логика валидации каждого продукта. Проверка на содержание запрещенных слов и другие аспекты.

### Заказ

Реализована mock система оплаты и многоступенчатая система валидации заказа перед оплатой.

### Доставка
Реализована система передачи сохраненной доставки в курьерское приложение и распределение ближайшему свободному курьеру.
Вся информации о текущем состояние в процессе доставки передаётся от курьерского приложения к клиентскому для удобства отслеживания.

При обнаружении возможного опоздания доставки высылается уведомление курьеру с просьбой поторопиться.

### Курьер

На данный момент есть сырая реализация регистрации в боте, трекинга местоположения, выхода на линию, получения заказ, 
завершения заказа с получением награды, выхода с линии.

При активации бота для куерьра автоматически создаётся профиль в базе данных. При выходе на линии система подбирает заказ
для курьера, отталкиваюсь от его текущего местоположения. При успешном завершении заказа начисляется награда.

При назначении курьеру доставки высылается сообщение с координатами где нужно забрать заказ - высылается сообщение с обновлением статуса заказа на 
клиентский сервис, после отметки о получении заказа высылается сообщение с координатами куда нужно отнести заказ, повторно высылается сообщение с обновлением статуса заказа.


## Инфраструктура

Для разворачивания инфраструктуры приложения используется Docker Compose
Для ускорение процесса разработки написан Makefile со скриптами часто используемых сценариев

### Связь сервисов

- Kafka, Zookeeper - для общения между сервисом маркетплейса и службой доставки: получение данных о состоянии заказа, информации о курьере
и real-time трекинг передвижений.

### Хранилища

- PostgreSQL - основная база данных
- Redis - для кеша и в качестве message брокера для Celery

### Фоновые задачи

- Celery - для обеспечения скорости работы приложения. Многие операции, которые потенциально могут нести высокие
нагрузки выведены в background задачи.

### Курьерское приложение

- Telegram Bot - обеспечивает очень удобную и быструю процедуру регистрации в качестве курьера для любого желающего заработать, а также
удобный инструмент для отслеживания действий курьеров.

## Стиль написания

При разработке придерживаюсь best-practise в разработке REST API, использую шаблоны проектирования и следую принципам SOLID, DRY, KISS.
Настроены pre-commit хуки, линтеры для поддержания единообразия стиля кода и обнаружения ошибок на ранних этапах разработки.

## Оптимизация

Проводится оптимизация SQL запросов. 
Исправлены n+1 ошибки, исправлено избытычное обращение к базе данных.

## Тестирование

Написание кода ведется с учетом TDD, каждая логическая строка кода сначала покрывается юнит тестами.

### Тестирование загрузки товаров для магазина
- На данный момент проведено тестирование в условиях загрузки таблицы со 100000 продуктов и 
валидацией каждого из продуктов - клиент не заметил никаких изменений в работе приложения. (В дальнейшем планируется автоматизация
повышения выделяемых ресурсов и количества worker-ов при увелечении нагрузок на сервис)
