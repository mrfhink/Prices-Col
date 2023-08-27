# -*- encoding: utf-8 -*-

from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def extract_data(html,vendor):
    soup = BeautifulSoup(html, 'html.parser')
    products = []
    print(f"Buscando productos en {vendor['vendor_name']}...")
    for product in soup.find_all(vendor['products'][0], {vendor['products'][1]: vendor['products'][2]}):
        try:
            name = product.find(vendor['name'][0], {vendor['name'][1]: vendor['name'][2]}).text
            price_total = product.find(vendor['price'][0], {vendor['price'][1]: vendor['price'][2]}).text
            price_un = product.find(vendor['price_un'][0], {vendor['price_un'][1]: vendor['price_un'][2]}).text
            products.append({'name': name, 'price': price_total, 'price un': price_un})
        except:
            pass
            #print(f"Producto no encontrado en {vendor['vendor_name']}")
    return products

def cleanup(dataframe):
    re_pattern = re.compile(r"[^0-9,]", re.I)
    return re.sub(re_pattern, "", dataframe).replace("  ", " ").strip()

# Define a function to retrieve the HTML page for a given URL
def get_html(url, chrome_options):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)
    html = driver.page_source

    return html


def main():
    vendorD1={
        "products": ["div", "class", "styles__StyledCard-sc-3jvmda-0 LSTlO"],
        "name": ["p", "class", "CardName__CardNameStyles-sc-147zxke-0 bWeSzf prod__name"],
        "price": ["p", "class", "CardBasePrice__CardBasePriceStyles-sc-1dlx87w-0 bhSKFL base__price"],
        "price_un":["p","class","styles__PumStyles-sc-omx4ld-0 CardPum__CardPumStyles-sc-1vz27ac-0 eqiAgH RAFHO"],
        "vendor_name":"D1"
        }

    vendorFalabella={
        "products": ["div", "class", "jsx-1833870204 jsx-3831830274 pod pod-4_GRID"],
        "name": ["b", "class", "jsx-1833870204 copy2 primary  jsx-2889528833 normal       pod-subTitle subTitle-rebrand"],
        "price": ["li", "class", "jsx-2112733514 prices-1"],
        "price_un":["label","class","currency"],
        "vendor_name":"Falabella"
        }

    vendorExito={
        "products": ["div", "class", "vtex-flex-layout-0-x-flexColChild vtex-flex-layout-0-x-flexColChild--product-info pb0"],
        "name": ["h3", "class", "vtex-store-components-3-x-productNameContainer mv0 t-heading-4"],
        "price": ["div", "class", "exito-vtex-components-4-x-PricePDP"],
        "price_un":["span","class","exito-vtex-components-4-x-currencyContainer"],
        "vendor_name":"Exito"
        }

    vendorPricesmart={
        "products": ["div", "class", "search-product-info"],
        "name": ["p", "id", "product-name"],
        "price": ["strong", "id", "product-price"],
        "price_un":["label","class","currency"],
        "vendor_name":"Pricesmart"
        }

    vendorJumbo={
        "products": ["article", "class", "vtex-product-summary-2-x-element pointer pt3 pb4 flex flex-column h-100"],
        "name": ["h3", "class", "vtex-product-summary-2-x-productNameContainer mv0 vtex-product-summary-2-x-nameWrapper overflow-hidden c-on-base f5"],
        "price": ["div", "class", "tiendasjumboqaio-jumbo-minicart-2-x-price"],
        "price_un":["span","class","tiendasjumboqaio-calculate-pum-2-x-currencyContainer tiendasjumboqaio-calculate-pum-2-x-currencyContainer--shelf"],
        "vendor_name":"Jumbo"
        }
        
    # Setup chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")

    # Define the product to search for
    print("")
    query = str(input('Ingrese producto a buscar: '))
    product_name = query.replace(' ','%20')
    product_name_1 = query.replace(' ','+')
    print("")

    # Define the URLs for each online retailer
    exito_url = f"https://www.exito.com/{product_name}?_q={product_name}&map=ft"
    jumbo_url = f"https://tiendasjumbo.co/{product_name}?_q={product_name}&map=ft"
    falabella_url = f"https://falabella.com.co/falabella-co/search?Ntt={product_name_1}"
    d1_url = f"https://domicilios.tiendasd1.com/search?name={product_name}"
    pricesmart_url = f"https://www.pricesmart.com/site/co/es/busqueda?_sq={product_name_1}"

    # Scrape the web pages for each retailer and extract the product data

    exito_html = get_html(exito_url, chrome_options)
    exito_products = extract_data(exito_html,vendorExito)

    jumbo_html = get_html(jumbo_url, chrome_options)
    jumbo_products = extract_data(jumbo_html,vendorJumbo)

    falabella_html = get_html(falabella_url, chrome_options)
    falabella_products = extract_data(falabella_html,vendorFalabella)

    d1_html = get_html(d1_url, chrome_options)
    d1_products = extract_data(d1_html,vendorD1)

    pricesmart_html = get_html(pricesmart_url, chrome_options)
    pricesmart_products = extract_data(pricesmart_html,vendorPricesmart)

    print("")

    # Combine the data into a single dataframe
    data = []

    data = [{'Vendedor': 'Exito', 'Producto': product['name'], 'Precio': product['price'], 'Precio unidad':product['price un']} for product in exito_products]
    data += [{'Vendedor': 'Tiendas Jumbo', 'Producto': product['name'], 'Precio': product['price'], 'Precio unidad':product['price un']} for product in jumbo_products]
    data += [{'Vendedor': 'Falabella', 'Producto': product['name'], 'Precio': product['price'], 'Precio unidad':product['price un']} for product in falabella_products]
    data += [{'Vendedor': 'D1', 'Producto': product['name'], 'Precio': product['price'], 'Precio unidad':product['price un']} for product in d1_products]
    data += [{'Vendedor': 'Pricesmart', 'Producto': product['name'].split("\n                    ")[1], 'Precio': product['price'], 'Precio unidad':product['price un']} for product in pricesmart_products]

    # Cleaning up data
    df = pd.DataFrame(data)
    df['Precio unidad'] = df['Precio unidad'].str.split(pat = '$').str[1].apply(cleanup)
    df['Precio'] = df['Precio'].str.split('$').str[1].apply(cleanup)
    df['Precio unidad'] = df['Precio unidad'].str.replace(',','.')
    df['Precio'] = df['Precio'].str.replace(',','.')
    df['Precio unidad'] = pd.to_numeric(df['Precio unidad'],errors='coerce')#.map('   ${:,}'.format)
    df['Precio'] = pd.to_numeric(df['Precio'],errors='coerce')#.map('   ${:,}'.format)
    df=df.sort_values('Precio unidad')

    # Display the data in a table
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()