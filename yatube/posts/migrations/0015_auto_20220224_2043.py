# Generated by Django 2.2.16 on 2022-02-24 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0014_auto_20220222_2114'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-pub_date'], 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='follow',
            options={'ordering': ['user'], 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
    ]
