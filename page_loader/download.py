import os
import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


TAGS_AND_ATTRIBUTES = {
        'img': ('src', 'href'),
        'script': ('src',),
        'link': ('src', 'href'),
    }


def get_url_without_scheme(url):
    return url.split('//')[1]


def get_correct_name_and_ext(page_url):
    file_name, ext = os.path.splitext(page_url)
    file_name = re.sub("[^A-Za-z0-9]", "-", file_name)
    return file_name, ext


def get_data(page_url, child):
    data = requests.Session().get(page_url)
    if child:
        return data.content
    return data.text


def get_scheme_and_netloc_url(url):
    url = urlparse(url)
    return url.scheme, url.netloc


def download_link(file, download_folder, scheme, host, tags_and_attributes=TAGS_AND_ATTRIBUTES):

    def get_download_and_replace_link(search_tag, atr):
        tags = page_data.find_all(search_tag)
        for tag in tags:
            link = tag.get(atr)
            if link:
                _, link_netloc = get_scheme_and_netloc_url(link)
                if host in link_netloc:
                    new_name = download_page(link, download_folder, child=True)
                    name_download_folder = os.path.relpath(os.getcwd())
                    tag[atr] = os.path.join(name_download_folder, new_name)
                elif not link.startswith(scheme):
                    link = urljoin(f'{scheme}://{host}', link)
                    new_name = download_page(link, download_folder, child=True)
                    name_download_folder = os.path.relpath(os.getcwd())
                    tag[atr] = os.path.join(name_download_folder, new_name)
    with open(file) as f:
        page_data = BeautifulSoup(f, 'html.parser')
    for tag, attrs in tags_and_attributes.items():
        for attr in attrs:
            get_download_and_replace_link(tag, attr)
    page_data = page_data.prettify()
    with open(file, 'w') as f:
        f.write(page_data)


def download_page(page_url, download_path, child=False):
    url_without_scheme = get_url_without_scheme(page_url)
    file_name, _ = get_correct_name_and_ext(url_without_scheme)
    if not download_path:
        download_path = os.getcwd()
    file_path = os.path.join(download_path, file_name + '.html')
    data = get_data(page_url, child)
    if child:
        with open(file_path, 'wb') as f:
            f.write(data)
    else:
        with open(file_path, 'w') as f:
            f.write(data)
        download_folder = os.path.join(download_path, file_name + '_files')
        os.mkdir(download_folder)
        scheme, netloc = get_scheme_and_netloc_url(page_url)
        download_link(file_path, download_folder, scheme, netloc)
    return file_name


def download(page_url, download_path):
    return download_page(page_url, download_path)


# заменить папку для скачинвания (не полный путь, а относительный)
# проверить, что там с расширениями у файлов