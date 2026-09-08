from django.db import migrations


CATEGORIES = [
    ('Tech', 'tech'),
    ('Lifestyle', 'lifestyle'),
    ('Cosmetics', 'cosmetics'),
    ('Fashion', 'fashion'),
    ('Home & Living', 'home-living'),
    ('Sports & Outdoors', 'sports-outdoors'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    for name, slug in CATEGORIES:
        Category.objects.get_or_create(slug=slug, defaults={'name': name})


def remove_categories(apps, schema_editor):
    Category = apps.get_model('store', 'Category')
    Category.objects.filter(slug__in=[slug for _, slug in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_product_category'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
