__author__ = "Artyom Breus"
__copyright__ = "Copyright 2023, Khabarovsk"
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Artyom Breus"
__email__ = "Artyom.Breus@gmail.com"
__status__ = "Production"

# TOOL to get short summary for long article (using YandexGPT AI)
#
# REGULATION OF API: https://yandex.ru/legal/300ya_termsofuse/
# READ FIRST to get YandexGPT_API_token -> https://300.ya.ru/#
#
# USAGE: summary -h
# 	 summary <article_url>
#        summary <article_url> -t YandexGPT_API_token
#        summary <article_url> -t YandexGPT_API_token -o plain_text.txt

import requests
from pprint import pprint
from sys import exit, argv
from os import path as os_path
from datetime import datetime
from bs4 import BeautifulSoup
from argparse import ArgumentParser


YANDEX_GPT_API = "https://300.ya.ru/api/sharing-url"


def check_200_status(response):
    if response.status_code != 200:
        error = "ERROR: " + str(response)
        if response.request.method == "POST":
            error += str(response.json())
        pprint(error)
        exit(1)


def get_arguments():
    parser = ArgumentParser(description="Get summary a article conclusion")
    try:
        from ad_user import yandex_gpt_token
    except ModuleNotFoundError:
        token_storage_file = os_path.join(os_path.abspath(__file__), "ad_user.py")
        open(token_storage_file, "w", encoding="utf8").write(yandex_gpt_token="")
        yandex_gpt_token = ""

    parser.add_argument("site_url", type=str, help="Source URL")
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        default=yandex_gpt_token,
        help="YandexGPT token (https://300.ya.ru)",
    )
    parser.add_argument("-o", "--output", type=str, default="", help="Output filename")
    args = parser.parse_args()
    if not args.token:
        print(
            "ERROR: Not found YandexGPT API token - get it from https://300.ya.ru/ (API)"
        )
        exit(1)
    return args


def get_summary_url(site_url, yandex_gpt_token):
    # site_url = 'https://habr.com/ru/news/729422/'
    # site_url = 'https://habr.com/ru/articles/599039/'
    # site_url = 'https://remontcompa.ru/windows/windows-11/2571-kak-sozdat-ustanovochnuju-fleshku-windows-11-dlja-kompjuterov-bez-uefi-secure-boot-i-tpm-20-s-pomoschju-utility-rufus.html'

    response = requests.post(
        YANDEX_GPT_API,
        json={"article_url": site_url},
        headers={"User-Agent": "+++", "Authorization": f"OAuth {yandex_gpt_token}"},
    )

    check_200_status(response)

    # { #  "status": "success", #  "sharing_url": "https://300.ya.ru/BlaBlaBla" #}
    response = response.json()

    if response["status"] != "success":
        print("ERROR :", end="\t")
        pprint(response.json())
        exit(1)

    return response["sharing_url"]


def get_summary_content(summary_url, yandex_gpt_token):
    response = requests.get(
        summary_url,
        headers={"User-Agent": "+++", "Authorization": f"OAuth {yandex_gpt_token}"},
    )
    check_200_status(response)
    return response.content


def parse_summary(summary_content):
    soup = BeautifulSoup(summary_content, "html.parser")
    text = soup.find("meta", property="og:description").attrs["content"]
    return text


def run():
    args = get_arguments()
    summary_url = get_summary_url(args.site_url, args.token)
    summary_content = get_summary_content(summary_url, args.token)
    summary = parse_summary(summary_content)
    if args.output:
        with open(args.output, "w", encoding="utf8") as f:
            f.write(summary)
    else:
        print(summary)


if __name__ == "__main__":
    run()
