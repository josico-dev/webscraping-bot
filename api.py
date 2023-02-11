"""Module providingFunction web scraping for the website dontorrent"""
import re
import os

from bs4 import BeautifulSoup
import requests
from transmission_rpc import Client, TransmissionError

TR_USER = os.environ["TR_USER"]
TR_PASS = os.environ["TR_PASS"]
DOWNLOAD_DIR = os.environ["DOWNLOAD_DIR"]


class Dontorrent:
    """Class to scrape the website dontorrent"""

    URL = os.environ["DONTORRENT_URL"]
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) \
            Gecko/20100101 Firefox/109.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9, \
            image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": URL,
        "DNT": "1",
        "Connection": "keep-alive",
        "Cookie": "telegram=true",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }

    def __init__(self, url=URL):
        self.url = url
        self.headers = self.HEADERS

    def get_hrefs(self, search):
        """Get the hrefs of the search results"""
        try:
            page = requests.get(
                self.url + "/buscar/" + search, headers=self.headers, timeout=5
            )
        except requests.exceptions.Timeout:
            return None
        soup = BeautifulSoup(page.content, "html.parser")
        links = soup.find_all("a", class_="text-decoration-none")
        # create and return a duple list with the link and the text
        if len(links) == 0:
            return None

        return [(link.get_text(), link.get("href")) for link in links]

    def get_episodes(self, href, title):
        """Given the correct href, get the episodes"""
        search_url = self.url + href

        try:
            page = requests.get(search_url, headers=self.headers, timeout=5)
        except requests.exceptions.Timeout:
            return None

        soup = BeautifulSoup(page.content, "html.parser")
        if len(soup.find_all("tbody")) == 0:
            return None
        tr_tags = soup.findAll("tbody")[0].findAll("tr")

        if len(tr_tags) == 0:
            return None

        episodes = []
        for tr_tag in tr_tags:
            episodes.append(
                TorrentEpisode(
                    tr_tag.find("td").get_text(),
                    "https:" + tr_tag.find("a", id="download_torrent").get("href"),
                    title,
                )
            )
        return episodes

    def download_torrent(self, episode):
        """Download the torrent"""
        try:
            transmission_client = Client(
                host="127.0.0.1",
                port=9091,
                username=TR_USER,
                password=TR_PASS,
            )
            transmission_client.add_torrent(
                episode.magnet, download_dir=episode.get_download_path()
            )
        except TransmissionError as error_t:
            print(error_t)
            print("Error connecting to transmission")
            return False
        return True

    def show_downloads(self):
        """Show the downloads"""
        try:
            transmission_client = Client(
                host="127.0.0.1",
                port=9091,
                username=TR_USER,
                password=TR_PASS,
            )
        except TransmissionError as error_t:
            print(error_t)
            print("Error connecting to transmission")
            return False
        downloads = transmission_client.get_torrents()
        for download in downloads:
            print(download)
        return True


class TorrentEpisode:
    """Class to store the torrent episode"""

    def __init__(self, name, magnet, title):
        self.name = name
        self.magnet = magnet
        self.title = title.title()
        self.season = int(re.search(r"(\d+)x(\d+)", name).group(1))
        self.episode = int(re.search(r"(\d+)x(\d+)", name).group(2))
        self.path = f"{self.title}/Season {self.season}/{self.season}-{self.episode}"

    def __str__(self):
        return f"Name: {self.name} Magnet: {self.magnet}"

    def __repr__(self):
        return f"Name: {self.name} Magnet: {self.magnet}"

    def get_download_path(self):
        """Return the path to download the torrent, if not exist create it"""
        # check if path exists
        if not os.path.exists(self.path):
            os.makedirs(os.path.join(DOWNLOAD_DIR, self.path))
        return os.path.join(DOWNLOAD_DIR, self.path)
