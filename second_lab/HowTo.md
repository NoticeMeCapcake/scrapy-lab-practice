# Как запустить?

1. Установить poetry
2. Запустить `poetry install` (находясь в директории second_lab)
2. Запустить `docker-compose.yaml`
2. Перейти в директорию `/books_crawlwer/books_crawler`
3. Запустить `poetry run scrapy crawl books`
4. После завершения перейти в `/fast_api` директорию
5. Запустить `poetry run uvicorn library_service_api:app`
6. В отдельном терминале запустить запрос, например, `curl "http://127.0.0.1:8000/book?isbn=978-985-19-8454-7"`