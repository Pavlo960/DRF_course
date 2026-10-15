from django.db import migrations, models


def copy_menu_prices(apps, schema_editor):
    Order = apps.get_model('pub', 'Order')
    for order in Order.objects.select_related('menu_item'):
        order.price_per_liter = order.menu_item.price_per_liter
        order.save(update_fields=['price_per_liter'])


class Migration(migrations.Migration):

    dependencies = [
        ('pub', '0003_order_decimal_volume_optional_customer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'New'), ('preparing', 'Preparing'), ('served', 'Served'), ('cancelled', 'Cancelled')], default='new', max_length=20),
        ),
        # Added as nullable first, filled from the current menu prices, then made required
        migrations.AddField(
            model_name='order',
            name='price_per_liter',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
        migrations.RunPython(copy_menu_prices, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='order',
            name='price_per_liter',
            field=models.DecimalField(decimal_places=2, max_digits=6),
        ),
    ]
