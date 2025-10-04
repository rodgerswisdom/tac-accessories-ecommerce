from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
import logging

from checkout.models import Order, OrderItem
from catalog.models import Product

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def order_created_or_updated(sender, instance, created, **kwargs):
    """Log order creation and updates"""
    if created:
        logger.info(f"New order created: {instance.order_number} by {instance.customer}")
    else:
        logger.info(f"Order updated: {instance.order_number} - Status: {instance.status}")


@receiver(post_save, sender=OrderItem)
def order_item_created(sender, instance, created, **kwargs):
    """Log order item creation"""
    if created:
        logger.info(f"Order item added: {instance.product.name} x {instance.quantity} to order {instance.order.order_number}")


@receiver(post_delete, sender=Product)
def product_deleted(sender, instance, **kwargs):
    """Log product deletion"""
    logger.warning(f"Product deleted: {instance.name} (SKU: {instance.sku})")


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    """Log user creation"""
    if created:
        logger.info(f"New user registered: {instance.username} ({instance.email})")
