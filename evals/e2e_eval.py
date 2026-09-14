def evaluate_e2e(requirement,product):
    requirement_accuracy = requirement["accuracy"]
    product_score = product["score"]
    overall_score = (requirement_accuracy + product_score) / 2


    return overall_score


