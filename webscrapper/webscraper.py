from bs4 import BeautifulSoup
import requests
import pandas as pd
from database import connect, rec_insert, succ_insert, show_res, rec_del



class Data:
    def __init__(self, search):
        self.search_str = search

    def creating_link(self):
        base_url = "https://www.flipkart.com"

        search_url = f"{base_url}/search?q={self.search_str}"

        source1 = requests.get(search_url).text
        full_page = BeautifulSoup(source1, 'lxml')

        lst = []
        try:
            for division in full_page.find_all('div', class_="_1AtVbE col-12-12"):
                for div in division.find_all('div', class_="_2kHMtA"):
                    for anchors in div.find_all('a', class_="_1fQZEK"):
                        anchor = anchors['href']
                        lst.append(anchor)
        except Exception as err:
            print(err)

        # Taking only the top 3 products results
        lst = lst[:3]
        lst2 = []
        for i in range(len(lst)):
            prod_url = search_url + lst[i]
            lst2.append(prod_url)

        com_urls = []
        try:
            for i in range(len(lst2)):
                source2 = requests.get(lst2[i]).text
                prod_page = BeautifulSoup(source2, 'lxml')

                try:
                    for division in prod_page.find_all('div', class_="_1YokD2 _3Mn1Gg"):
                        for big_box in division.find_all('div', class_="_1AtVbE col-12-12"):
                            for box in big_box.find_all('div', class_="col JOpGWq"):
                                anchors = box.find_all('a')
                                anchor = anchors[-1]
                                prod_link = anchor['href']
                                rev_url = base_url + prod_link

                                # Taking comments from 1st to 10th review pages for each product
                                urls = []
                                for var in range(1, 11):
                                    url = [rev_url + "&page=%i" % var]
                                    urls.append(url[0])

                                for n in range(len(urls)):
                                    com_urls.append(urls[n])

                except Exception as err:
                    print(err)
        except Exception as err:
            print(err)

        return com_urls


    def data_fetching(self, urls):
        # Creating empty lists to store the data
        final = []
        page_no = []
        products = []
        prices = []
        buyers = []
        ratings = []
        headings = []
        comments = []

        try:
            for i in range(len(urls)):
                source = requests.get(urls[i]).text
                rev_page = BeautifulSoup(source, 'lxml')

                for col in rev_page.find_all('div', class_="col _2wzgFH K0kLPL"):
                    page = i + 1
                    page_no.append(page)
                    product = rev_page.find('div', class_="_2s4DIt _1CDdy2").text
                    prod_name = product.replace("Reviews", "")
                    products.append(prod_name)
                    price = rev_page.find('div', class_="_30jeq3").text
                    prices.append(price)
                    buyer = col.find('div', class_="row _3n8db9").find('div', class_="row").find('p', class_="_2sc7ZR _2V5EHH").text
                    buyers.append(buyer)
                    rating = col.find('div', class_="row").div.text
                    ratings.append(rating)
                    header = col.div.p.text
                    headings.append(header)
                    comment = col.find('div', class_="t-ZTKy").div.div.text
                    comments.append(comment)

        except Exception as err:
            print(err)
        else:
            mydict = ({'Page': page_no, 'Product': products, 'Price': prices, 'Buyer': buyers, 'Rating': ratings,'Header': headings, 'Comment': comments})
            final.append(mydict)
        return final


    def create_df(self, l):
        for r in l:
            df = pd.DataFrame(r)
        return df


    def loading_server(self, df):
        collection = connect()

        for (row, rs) in df.iterrows():
            page = rs[0]
            product = rs[1]
            price = rs[2]
            buyer = rs[3]
            rating = rs[4]
            header = rs[5]
            comment = rs[6]

            d = {
                "Page_no": page,
                "Product_name": product,
                "Unit Price": price,
                "User": buyer,
                "Ratings": rating,
                "Comment_head": header,
                "Comments": comment
            }

            rec_insert(collection, d)
        succ_insert(collection)


    def data_show(self):
        collection = connect()
        try:
            results = show_res(collection)
        except Exception as e:
            pass
        else:
            return results


    def data_del(self):
        collection = connect()
        rec_del(collection)
