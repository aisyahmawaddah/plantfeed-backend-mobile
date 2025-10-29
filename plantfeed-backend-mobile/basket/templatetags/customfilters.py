from django import template
from member.models import Person

register = template.Library()

@register.filter
def get_subtotal(subtotals, product_id):
    return subtotals.get(product_id)

@register.filter
def get_seller(sellers, product_id):
    return sellers.get(product_id)

@register.filter
def get_username_from_id(person_id):
    try:
        person = Person.objects.get(id=person_id)
        return person.Username
    except Person.DoesNotExist:
        return "Unknown"  # or handle the case when the person does not exist
    
@register.filter
def get_sellerTotal(sellerTotal, product_id):
    return sellerTotal.get(product_id)
