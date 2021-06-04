"""CairnReader parses the pages you ask him to for the request you entered on the French platform Cairn.org.
It then puts data about the articles title, publisher, author and data for you in a .csv, gives you the top 20
authors and publishers in the console, and bars the main authors for you.
Make sure you have a Web Driver in your directory !"""
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from tkinter import *
import pandas as pd
import re
from matplotlib import pyplot as plt


class CairnReader:
    def __init__(self):
        self.data_request = ""
        self.page_request = ""
        self.pages_max = 1
        self.root = Tk()
        self.root.title("Enter here your search and page count !")
        self.search_title = Label(self.root, text="Enter your search (in French if you want it to work...) :")
        self.textBox1 = Text(self.root, height=10, width=40)
        self.page_count = Label(self.root, text="Enter the number of pages you want to parse (>1) :")
        self.textBox2 = Text(self.root, height=10, width=40)
        self.warning = Label(self.root, text="Prepare yourself for some puzzle and cookie accepting... \n This "
                                             "program will parse those pages for Title, Publisher, Author and Date, "
                                             "and put them in a .csv called 'bibliography.csv' for you to study in R. "
                                             "\n Then, it will give you the top 20 authors and publishers, "
                                             "and plot the authors' bars.")
        self.buttonRecherche = Button(self.root, height=1, width=10, text="Let's go !",
                                      command=lambda: CairnReader.request_data(self))
        self.pages = 0
        self.cairn_titles = []
        self.cairn_authors = []
        self.cairn_publishers = []
        self.cairn_dates = []
        self.url = ""
        self.html = ""
        self.data = []
        self.count_publishers = []
        self.count_authors = []

    def cairn_parser(self, arg):
        soup = BeautifulSoup(self.html, 'lxml')
        for element in soup.find_all('div', {"class": "article-meta"}):
            if element.find('li', {"class": "titre-article"}) is not None:
                titre = element.find('li', {"class": "titre-article"}).text
            else:
                if element.find('li', {"class": "titre-numero"}) is not None:
                    titre = element.find('li', {"class": "titre-numero"}).text
                else:
                    if element.find('li', {"class": "titre"}) is not None:
                        titre = element.find('li', {"class": "titre"}).text
                    else:
                        titre = 'NA'
            self.cairn_titles.append(titre)
            if element.find('li', {"class": "auteurs"}) is not None:
                author = element.find('li', {"class": "auteurs"}).text
            else:
                author = 'Collective'
            self.cairn_authors.append(author)
            if element.find('span', {"class": "titre-revue"}):
                publisher = element.find('span', {"class": "titre-revue"}).text
            else:
                if element.find('li', {"class": "meta"}) is not None:
                    publisher = element.find('li', {"class": "meta"}).text
                    publisher = re.sub(r"\d", r"", publisher)
                    publisher = re.sub(r"\W", r" ", publisher)
                else:
                    publisher = 'NA'
            self.cairn_publishers.append(publisher)
            if element.find('li', {"class": "meta"}) is not None:
                # if article.find('li', {"class": "meta"}).a.a is not None:
                # year = article.find('li', {"class": "meta"}).a.a
                year = element.find('li', {"class": "meta"}).text
                year = re.sub(r"\D", r"", year)
                year = year[:4]
            else:
                year = 'NA'
            self.cairn_dates.append(year)
        df = pd.DataFrame(list(zip(self.cairn_titles, self.cairn_authors, self.cairn_publishers, self.cairn_dates)),
                          columns=['Title', 'Author', 'Publisher', 'Date'])
        df.to_csv('bibliography.csv', header=True, index=False)

    def request_data(self):
        self.data_request = self.textBox1.get("1.0", "end-1c")
        self.textBox1.quit()
        self.page_request = self.textBox2.get("1.0", "end-1c")
        self.pages_max = int(self.page_request)
        self.data_request = self.data_request.lower()
        self.data_request = re.sub(r" ", "+", self.data_request)
        print("Prepare yourself for some puzzle and cookie accepting... This program will parse those pages for "
              "Title, Publisher, Author and Date, and put them in a csv. Then, it will give you the top 20 authors "
              "and publishers, and plot the authors' bars.")

    def cairn_driver(self):
        self.search_title.pack()
        self.textBox1.pack()
        self.page_count.pack()
        self.textBox2.pack()
        self.warning.pack()
        self.buttonRecherche.pack()
        self.root.mainloop()
        self.url = "https://www.cairn.info/resultats_recherche.php?searchTerm=+" + self.data_request
        options = Options()
        options.add_argument("window-size=1400,600")
        ua = UserAgent()
        user_agent = ua.random
        print(user_agent)
        options.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Firefox(executable_path="/DIRECTORY", options=options)
        driver.get(self.url)
        while True and self.pages < self.pages_max:
            try:
                self.pages = self.pages + 1
                time.sleep(5)
                self.html = driver.page_source
                time.sleep(5)
                self.cairn_parser(self.html)
                time.sleep(5)
                elm = driver.find_element_by_link_text('navigate_next')
                time.sleep(5)
                elm.click()
                time.sleep(5)
            except NoSuchElementException:
                break
        driver.close()

    def stats(self):
        self.data = pd.read_csv('bibliography.csv', sep=',')
        self.count_publishers = self.data['Publisher'].value_counts(ascending=False)
        self.count_authors = self.data['Author'].value_counts(ascending=False)
        print(self.count_publishers[:20])
        print(self.count_authors[:20])
        self.count_authors[:10].plot.bar()
        plt.show()


if __name__ == '__main__':
    CairnReader().cairn_driver()
    CairnReader().stats()
