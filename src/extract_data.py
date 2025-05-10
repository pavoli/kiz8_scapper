import asyncio
import json
import os

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from src.utils.logger import setup_logger
from src.utils.config import (
    API_URL,
    START_URL_TEMPLATE,
    RAW_DIR,
    JSON_DIR,
)

logger = setup_logger(level=10)
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)


async def async_parse_yeahub():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page_num = 1

        async def handle_response(response):
            if API_URL in response.url and response.status == 200:
                filename = os.path.join(JSON_DIR, f"page_{page_num}.json")
                json_data = await response.json()
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(json_data, file, ensure_ascii=False, indent=2)

        page.on("response", handle_response)

        while True:
            url = START_URL_TEMPLATE.format(page=page_num)
            print(f"Load page {page_num}: {url}")
            logger.debug(f"Load page {page_num}: {url}")
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

            filename = os.path.join(RAW_DIR, f"page_{page_num}.html")
            locator = page.locator("div.Ri4XE")
            count = await locator.count()

            data = ''
            for i in range(count):
                element = locator.nth(i)
                text = await element.text_content()
                rating_pos = text.find("Рейтинг")
                # complexity_pos = text.find("Сложность")
                question = text[:rating_pos]
                # rating = text[rating_pos:complexity_pos]
                answer_pos = text.find("Сложность") + 11
                answer = text[answer_pos:].replace("Подробнее", "")

                data += f"Вопрос {i+1}<br>"
                data += f"{question}<br>"
                data += "Ответ<br>"
                data += f"{answer}<br><br>"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(data)
            print(f"Saved: {filename}")
            logger.debug(f"Saved: {filename}")

            button = page.get_by_label("forward button")
            if await button.count() > 0:
                class_attr = await button.get_attribute("disabled")

                if class_attr is not None:
                    print("`Next` button is disabled, parsing finished.")
                    logger.warning("`Next` button is disabled, parsing finished.")
                    break
                page_num += 1
            else:
                print("`Next` button didn't find, parsing finished.")
                logger.warning("`Next` button didn't find, parsing finished.")
                break

        await browser.close()


def parse_yeahub():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page_num = 1

        def handle_response(response):
            if API_URL in response.url and response.status == 200:
                filename = os.path.join(JSON_DIR, f"page_{page_num}.json")
                json_data = response.json()
                with open(filename, 'w', encoding='utf-8') as file:
                    json.dump(json_data, file, ensure_ascii=False, indent=2)

        page.on("response", handle_response)

        while True:
            url = START_URL_TEMPLATE.format(page=page_num)
            print(f"Load page {page_num}: {url}")
            logger.debug(f"Load page {page_num}: {url}")
            page.goto(url)
            page.wait_for_load_state("networkidle")

            filename = os.path.join(RAW_DIR, f"page_{page_num}.html")
            locator = page.locator("div.Ri4XE")
            count = locator.count()

            data = ''
            for i in range(count):
                element = locator.nth(i)
                text = element.text_content()
                rating_pos = text.find("Рейтинг")
                # complexity_pos = text.find("Сложность")
                question = text[:rating_pos]
                # rating = text[rating_pos:complexity_pos]
                answer_pos = text.find("Сложность") + 11
                answer = text[answer_pos:].replace("Подробнее", "")

                data += f"Вопрос {i+1}<br>"
                data += f"{question}<br>"
                data += "Ответ<br>"
                data += f"{answer}<br><br>"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(data)
            print(f"Saved: {filename}")
            logger.debug(f"Saved: {filename}")

            button = page.get_by_label("forward button")
            if button.count() > 0:
                class_attr = button.get_attribute("disabled")

                if class_attr is not None:
                    print("`Next` button is disabled, parsing finished.")
                    logger.warning("`Next` button is disabled, parsing finished.")
                    break
                page_num += 1
            else:
                print("`Next` button didn't find, parsing finished.")
                logger.warning("`Next` button didn't find, parsing finished.")
                break

        browser.close()


if __name__ == "__main__":
    # asyncio.run(async_parse_yeahub())
    parse_yeahub()
