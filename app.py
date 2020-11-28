import requests
import time
import json
from datetime import datetime
import urllib.parse as urlparse
from urllib.parse import parse_qs
# import webhook_settings
# import product_settings
from threading import Thread
from selenium import webdriver
from chromedriver_py import binary_path as driver_path
from lxml import html
import os

stockdict = {}
sku_dict = {}
bestbuylist = []
targetlist = []
walmartlist = []
bhlist = []
bbdict = {}
bbimgdict = {}
amazonlist = []
gamestoplist = []


# Function for start-up menu
def menu():
    webhook_dict = return_data("./data/webhooks.json")
    url_dict = return_data("./data/products.json")
    # print("Select an Option: \n 1: Edit Webhooks \n 2: Edit Product URLs \n 3: Run the product tracker \n")
    # val = input("Enter # (1-3)")
    # if val == "1":
    #     webhook_settings.main()
    #     menu()
    # elif val == "2":
    #     product_settings.main()
    #     menu()
    # elif val == "3":
    #     print("\n \n Starting Product Tracker! \n \n")
    # else:
    #     menu()


def return_data(path):
    with open(path,"r") as file:
        data = json.load(file)
    file.close()
    return data

# Prompt the user at startup
menu()

# Only declare the webhook and product lists after the menu has been passed so that changes made from menu selections are up to date
webhook_dict = return_data("./data/webhooks.json")
url_dict = return_data("./data/products.json")


# Declare classes for the webpage scraping functionality
class Amazon:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"')
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--sandbox")

        # Heroku setup
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)

        # driver = webdriver.Chrome(executable_path=driver_path, options=options)
        driver.get(url)

        html = driver.page_source
        if "To discuss automated access to Amazon data please contact api-services-support@amazon.com." in html:
            print("Amazons Bot Protection is preventing this call.")
        else: 
            status_raw = driver.find_element_by_xpath("//div[@id='olpOfferList']")
            status_text = status_raw.text
            title_raw = driver.find_element_by_xpath("//h1[@class='a-size-large a-spacing-none']")
            title_text = title_raw.text
            title = title_text
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if "Currently, there are no sellers that can deliver this item to your location." not in status_text:
                print("[" + current_time + "] " + "In Stock: (Amazon.com) " + title + " - " + url)
                # slack_data = {'content': "[" + current_time + "] " +  title + " in stock at Amazon - " + url}
                img_raw = driver.find_element_by_xpath('//*[@id="olpProductImage"]/a/img')
                img =img_raw.get_attribute('src')
                slack_data = {
                    'username': "Amazon Bot",
                    'avatar_url': "https://github.com/tnware/product-checker/blob/master/img/amazon.png",
                    'content': "GameStop Stock Alert:",
                    'embeds': [{
                        'title': title,
                        'description': title + " in stock at Amazon",
                        'url': url,
                        "fields": [
                            {
                                "name": "Time:",
                                "value": current_time
                            },
                            {
                                "name": "Status:",
                                "value": "In Stock"
                            }
                        ],
                        'thumbnail': {
                            'url': img
                        }
                    }]
                }
                if stockdict.get(url) == 'False':
                    response = requests.post(
                        webhook_url, data=json.dumps(slack_data),
                        headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else:
                # print("[" + current_time + "] " + "Sold Out: (Amazon.com) " + title)
                stockdict.update({url: 'False'})
        driver.quit()


class Gamestop:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"')
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--sandbox")

        # Heroku setup
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)

        # driver = webdriver.Chrome(executable_path=driver_path, options=options)
        driver.get(url)
        # status_raw = driver.find_element_by_xpath("//div[@class='add-to-cart-buttons']")
        # status_text = status_raw.text
        status_raw = driver.find_elements_by_class_name('add-to-cart-buttons')
        status_text = status_raw[0].text
        title_raw = driver.find_element_by_xpath("//h1[@class='product-name h2']")
        title_text = title_raw.text
        title = title_text
        # image_raw = driver.find_element_by_xpath("//img[@class='mainImg']")
        # image_raw = driver.find_element_by_class_name('product-main-image-gallery')
        # img = image_raw.get_attribute('src')
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if "ADD TO CART" in status_text:
            print("[" + current_time + "] " + "In Stock: (Gamestop.com) " + title + " - " + url)
            slack_data = {
                'username': "GameStop Bot",
                'avatar_url': "https://github.com/tnware/product-checker/blob/master/img/gamestop.png",
                'content': "GameStop Stock Alert:", 
                'embeds': [{ 
                    'title': title,  
                    'description': title + " in stock at GameStop", 
                    'url': url, 
                    "fields": [
                    {
                        "name": "Time:",
                        "value": current_time
                    },
                    {
                        "name": "Status:",
                        "value": "In Stock"
                    }
                            ],
                    # 'thumbnail': {
                    #     'url': img
                    #     }
                    }]
                }
            if stockdict.get(url) == 'False':
                response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'})
            stockdict.update({url: 'True'})
        else:
            # print("[" + current_time + "] " + "Sold Out: (Gamestop.com) " + title)
            stockdict.update({url: 'False'})
        driver.quit()


class Target:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        page = requests.get(url)
        al = page.text
        tree = html.fromstring(page.content)
        imgs = tree.xpath("//img[1]")
        img_raw = str(imgs[0].attrib)
        img = img_raw[20:-2]
        title = al[al.find('"twitter":{"title":') + 20 : al.find('","card')]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if "Deliver to" not in page.text:
            # print("[" + current_time + "] " + "Sold Out: (Target.com) " + title)
            stockdict.update({url: 'False'})
        else: 
            print("[" + current_time + "] " + "In Stock: (Target.com) " + title + " - " + url)
            slack_data = {
                'username': "Target Bot",
                'avatar_url': "https://github.com/tnware/product-checker/raw/master/img/target.png",
                'content': "Target Stock Alert:", 
                'embeds': [{ 
                    'title': title,  
                    'description': title + " in stock at Target", 
                    'url': url, 
                    "fields": [
                    {
                        "name": "Time:",
                        "value": current_time
                    },
                    {
                        "name": "Status:",
                        "value": "In Stock"
                    }
                            ],
                    'thumbnail': { 
                        'url': img
                        }
                    }]
                }
            if stockdict.get(url) == 'False':
                response = requests.post(
                    webhook_url, data=json.dumps(slack_data),
                    headers={'Content-Type': 'application/json'})
            stockdict.update({url: 'True'})
        #print(stockdict)


class BestBuy:

    def __init__(self, sku, hook):
        self.sku = sku
        self.hook = hook
        webhook_url = webhook_dict[hook]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        url = "https://www.bestbuy.com/api/tcfb/model.json?paths=%5B%5B%22shop%22%2C%22scds%22%2C%22v2%22%2C%22page%22%2C%22tenants%22%2C%22bbypres%22%2C%22pages%22%2C%22globalnavigationv5sv%22%2C%22header%22%5D%2C%5B%22shop%22%2C%22buttonstate%22%2C%22v5%22%2C%22item%22%2C%22skus%22%2C" + sku + "%2C%22conditions%22%2C%22NONE%22%2C%22destinationZipCode%22%2C%22%2520%22%2C%22storeId%22%2C%22%2520%22%2C%22context%22%2C%22cyp%22%2C%22addAll%22%2C%22false%22%5D%5D&method=get"
        headers2 = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
        }
        page = requests.get(url, headers=headers2)
        link = "https://www.bestbuy.com/site/" + sku + ".p?skuId=" + sku
        al = page.text
        search_string = '"skuId":"' + sku + '","buttonState":"'
        stock_status = al[al.find(search_string) + 33: al.find('","displayText"')]
        product_name = sku_dict.get(sku)
        if stock_status == "SOLD_OUT":
            # print("[" + current_time + "] " + "Sold Out: (BestBuy.com) " + product_name)
            stockdict.update({sku: 'False'})
        elif stock_status == "CHECK_STORES":
            # print(product_name + " sold out @ BestBuy (check stores status)")
            stockdict.update({sku: 'False'})
        else: 
            if stock_status == "ADD_TO_CART":
                print("[" + current_time + "] " + "In Stock: (BestBuy.com) " + product_name + " - " + link)
                slack_data = {
                    'username': "BestBuy Bot",
                    'avatar_url': "https://github.com/tnware/product-checker/raw/master/img/bestbuy.png",
                    'content': "BestBuy Stock Alert:", 
                    'embeds': [{ 
                        'title': product_name,  
                        'description': product_name + " in stock at BestBuy", 
                        'url': link, 
                        "fields": [
                        {
                            "name": "Time:",
                            "value": current_time
                        },
                        {
                            "name": "Status:",
                            "value": "In Stock"
                        }
                                ],
                        'thumbnail': { 
                            'url': bbimgdict.get(sku)
                            }
                        }]
                    }
                if stockdict.get(sku) == 'False':
                    response = requests.post(
                        webhook_url, data=json.dumps(slack_data),
                        headers={'Content-Type': 'application/json'})
                stockdict.update({sku: 'True'})
                # print(stockdict)


class Walmart:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        # page = requests.get(url)
        # tree = html.fromstring(page.content)
        # title_raw = tree.xpath("//h1[@class='prod-ProductTitle font-normal']")
        # title = title_raw[0].text
        # price_raw = tree.xpath("//span[@class='price display-inline-block arrange-fit price price--stylized']//span[@class='price-characteristic']")
        # price = price_raw[0].text
        # img_raw = tree.xpath("//meta[@property='og:image']/@content")
        # img = img_raw[0]
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('log-level=3')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument(
            '--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"')
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--sandbox")

        # Heroku setup
        options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=options)

        # driver = webdriver.Chrome(executable_path=driver_path, options=options)
        driver.get(url)

        title = driver.find_element_by_xpath("//h1[@class='prod-ProductTitle prod-productTitle-buyBox font-bold']").text
        price = driver.find_element_by_xpath(
            "//span[@class='price display-inline-block arrange-fit price price--stylized']//span[@class='price-characteristic']").text
        img_raw = driver.find_element_by_xpath("//meta[@property='og:image']")
        img = img_raw.get_attribute('content')

        try:
            driver.find_element_by_xpath(
                '//*[@id="add-on-atc-container"]/div[1]/section/div[1]/div[3]/button/span/span')
            add_to_cart = True
        except:
            add_to_cart = False

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        if add_to_cart:
            print("[" + current_time + "] " + "In Stock: (Walmart.com) " + title + " for $" + price + " - " + url)
            slack_data = {
                'username': "Walmart Bot",
                'avatar_url': "https://github.com/tnware/product-checker/raw/master/img/walmart.png",
                'content': "Walmart Stock Alert:",
                'embeds': [{
                    'title': title,
                    'description': title + " in stock at Walmart for $" + price,
                    'url': url,
                    "fields": [
                    {
                    "name": "Time:",
                    "value": current_time
                    },
                    {
                        "name": "Price:",
                        "value": "$" + price
                    }
                            ],
                    'thumbnail': {
                        'url': img
                        }
                    }]
                }
            if stockdict.get(url) == 'False':
                try:
                    response = requests.post(
                        webhook_url, data=json.dumps(slack_data),
                        headers={'Content-Type': 'application/json'})
                except:
                    print("Webhook sending failed. Invalid URL configured.")
            stockdict.update({url: 'True'})
        else:
            print("[" + current_time + "] " + "Sold Out: (Walmart.com) " + title)
            stockdict.update({url: 'False'})

        driver.quit()


# TODO test and fix if necessary
class BH:

    def __init__(self, url, hook):
        self.url = url
        self.hook = hook
        webhook_url = webhook_dict[hook]
        page = requests.get(url)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if page.status_code == 200:
            if "Add to Cart" in page.text:
                print("[" + current_time + "] " + "In Stock: (bhphotovideo.com) " + url)
                slack_data = {'content': "[" + current_time + "] " + url + " in stock at B&H"}
                if stockdict.get(url) == 'False':
                    response = requests.post(
                                             webhook_url, data=json.dumps(slack_data),
                                             headers={'Content-Type': 'application/json'})
                stockdict.update({url: 'True'})
            else:
                print("[" + current_time + "] " + "Sold Out: (bhphotovideo.com) " + url)
                stockdict.update({url: 'False'})


# classify all the URLs by site
for url in url_dict:
    hook = url_dict[url] # get the hook for the url so it can be passed in to the per-site lists being generated below

    # Amazon URL Detection
    if "amazon.com" in url:
        if "offer-listing" in url:
            amazonlist.append(url)
            print("Amazon detected using Webhook destination " + hook)
        else:
            print("Invalid Amazon link detected. Please use the Offer Listing page.")

    # Target URL Detection
    elif "gamestop.com" in url:
        gamestoplist.append(url)
        print("Gamestop URL detected using Webhook destination " + hook)

    # BestBuy URL Detection
    elif "bestbuy.com" in url:
        print("BestBuy URL detected using Webhook destination " + hook)
        parsed = urlparse.urlparse(url)
        sku = parse_qs(parsed.query)['skuId']
        sku = sku[0]
        bestbuylist.append(sku)
        headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "cache-control": "max-age=0",
        "upgrade-insecure-requests": "1",
        "user-agent": " "
        }
        page = requests.get(url, headers=headers)
        al = page.text
        tree = html.fromstring(page.content)
        img = tree.xpath('//img[@class="primary-image"]/@src')[0]
        title = al[al.find('<title >') + 8 : al.find(' - Best Buy</title>')]
        sku_dict.update({sku: title})
        bbdict.update({sku: hook})
        bbimgdict.update({sku: img})

    # Target URL Detection
    elif "target.com" in url:
        targetlist.append(url)
        print("Target URL detected using Webhook destination " + hook)

    # Walmart URL Detection
    elif "walmart.com" in url:
        walmartlist.append(url)
        print("Walmart URL detected using Webhook destination " + hook)

    # B&H Photo URL Detection
    elif "bhphotovideo.com" in url:
        bhlist.append(url)
        print("B&H URL detected using Webhook destination " + hook)

# set all URLs to be "out of stock" to begin
for url in url_dict:
    stockdict.update({url: 'False'}) 
# set all SKUs to be "out of stock" to begin
for sku in sku_dict:
    stockdict.update({sku: 'False'})


# DECLARE SITE FUNCTIONS
def amazon_run(url):
    while True:
        hook = url_dict[url]
        try:
            Amazon(url, hook)
        except:
            print("Some error occurred parsing Amazon: "  + url)
        time.sleep(10)

def gamestop_run(url):
    while True:
        hook = url_dict[url]
        try:
            Gamestop(url, hook)
        except:
            print("Some error occurred parsing GameStop")
        time.sleep(10)


def target_run(url):
    while True:
        hook = url_dict[url]
        try:
            Target(url, hook)
        except:
            print("Some error occurred parsing Target")
        time.sleep(10)


def bh_run(url):
    while True:
        hook = url_dict[url]
        try:
            BH(url, hook)
        except:
            print("Some error occurred parsing BH Photo")
        time.sleep(10)


def bestbuy_run(sku):
    while True:
        hook = bbdict[sku]
        try:
            BestBuy(sku, hook)
        except:
            print("Some error occurred parsing Best Buy")
        time.sleep(10)


def walmart_run(url):
    while True:
        hook = url_dict[url]
        try:
            Walmart(url, hook)
        except:
            print("Some error occurred parsing WalMart")
        time.sleep(10)


# MAIN EXECUTION
for url in amazonlist:
    t = Thread(target=amazon_run, args=(url,))
    t.start()
    time.sleep(0.5)

for url in gamestoplist:
    t = Thread(target=gamestop_run, args=(url,))
    t.start()
    time.sleep(0.5)

for url in targetlist:
    t = Thread(target=target_run, args=(url,))
    t.start()
    time.sleep(0.5)

for url in bhlist:
    t = Thread(target=bh_run, args=(url,))
    t.start()
    time.sleep(0.5)

for sku in bestbuylist:
    t = Thread(target=bestbuy_run, args=(sku,))
    t.start()
    time.sleep(0.5)

for url in walmartlist:
    t = Thread(target=walmart_run, args=(url,))
    t.start()
    time.sleep(0.5)
