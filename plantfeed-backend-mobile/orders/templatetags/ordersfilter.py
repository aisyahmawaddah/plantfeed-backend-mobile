from django import template
from collections import defaultdict

register = template.Library()

@register.filter
def unique_combinations(allBasket):
    processed_combinations = set()
    unique_baskets = []
    for bas in allBasket:
        combination = (bas.transaction_code, bas.productid.Person_fk_id)
        if combination not in processed_combinations:
            processed_combinations.add(combination)
            unique_baskets.append(bas)
    return unique_baskets
