import os
import sys
import subprocess
import argparse
import shutil


template = """
# Парсер для {domain}

Запуск паука

```shell
scrapy crawl {spider_name} -O result.json
```

"""

def create_spider(spider_name, domain):
    # Проверяем, что скрипт выполняется в виртуальном окружении
    if not hasattr(sys, 'real_prefix') and not 'VIRTUAL_ENV' in os.environ:
        print("Ошибка: скрипт должен выполняться в виртуальном окружении!")
        sys.exit(1)

    # Получаем текущую рабочую директорию
    spiders_dir = os.path.join(os.getcwd(), "scrapy_project", "spiders")
    target_spider_dir = os.path.join(spiders_dir, spider_name)

    # Создаем директорию, если она не существует
    os.makedirs(target_spider_dir, exist_ok=True)

    # Создаем временного паука для последующего переименования
    command = ['scrapy', 'genspider', '-t', 'debug_parse', spider_name, domain]
    subprocess.run(command)

    _spider_file = os.path.join(spiders_dir, spider_name + ".py")
    shutil.move(_spider_file, target_spider_dir)

    os.rename(
        os.path.join(target_spider_dir, spider_name + ".py"),
        os.path.join(target_spider_dir, "spider.py"),
    )

    for item in ["settings.py", "__init__.py", "Readme.md"]:
        with open(os.path.join(target_spider_dir, item), "w") as f:
            if item == "Readme.md":
                f.write(template.format(domain=domain, spider_name=spider_name))

    # Переименовываем сгенерированный файл в main.py
    # os.rename(
    #     os.path.join(spider_dir, f'{temp_spider_name}.py'),
    #     os.path.join(spider_dir, 'main.py')
    # )

    # print(f"Spider '{spider_name}' создан в {spider_dir}/main.py")

def main():
    parser = argparse.ArgumentParser(description="Создать Scrapy паука в определенной структуре")
    parser.add_argument('spider_name', help="Имя паука, которое будет использовано для названия директории")
    parser.add_argument('domain', help="Домен, для которого создается паук")

    args = parser.parse_args()

    create_spider(args.spider_name, args.domain)

if __name__ == '__main__':
    main()