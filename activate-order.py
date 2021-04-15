import requests

# GoogleSheets lookup table
GoogleSheets_APIKEY = "..."
Google_ClientID = "..."
Google_ClientSecret = "..."
GoogleSheet_API = "..."
sheet_request = requests.get(GoogleSheet_API).json()
googlesheet_rows = sheet_request["values"]

# Parse googlesheet into two dictionaries
kajabi_ids = {}
shopify_skus = {}

for row in googlesheet_rows:
    kajabi_key = row[0]
    value = row[1]
    shopify_key = row[3]

    kajabi_ids.update({kajabi_key: value})
    shopify_skus.update({shopify_key: value})

print(len(googlesheet_rows), " products read from lookup table.")

# Shopify API
API_KEY = "..."
PASSWORD = "..."
shop_url = "..." % (API_KEY, PASSWORD)


while True:    
    order_number = input("Order #")

    shopify_orders = requests.get(
        shop_url,
        params = { "status": "any", "name": order_number}
            ).json()

    email = shopify_orders["orders"][0]["email"]
    first_name = shopify_orders["orders"][0]["customer"]["first_name"]
    last_name = shopify_orders["orders"][0]["customer"]["last_name"]
    full_name = first_name + " " + last_name
    purchased_products = shopify_orders["orders"][0]["line_items"]

    print(email, first_name, last_name)

    payload = {'external_user_id': email,'name': full_name, 'email': email}

    # activate each item in Kajabi
    for item in purchased_products:
        product_id = item["sku"]
        title = item["title"]

        if product_id in kajabi_ids:
            webhook = kajabi_ids[product_id]

        elif product_id in shopify_skus:
            webhook = shopify_skus[product_id]

        else:
            print("Product not found: ", title)
            continue
            
        kajabi_request = requests.post(webhook, data=payload, params={"send_offer_grant_email": "true"}).json()
        
        print("* ", title, " -> ", kajabi_request["status"])
    
    print("-------------------------------------------------------------------\n")
