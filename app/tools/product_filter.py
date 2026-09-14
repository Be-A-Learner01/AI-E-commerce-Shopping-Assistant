from app.tools.product_match import match_product
def filter_products(products, requirements):
    filtered_products = []

    for item in products:
        product = item["document"].metadata["product"]

        matched,_ = match_product(product,requirements)

        if matched:
            filtered_products.append(item)

    return filtered_products
