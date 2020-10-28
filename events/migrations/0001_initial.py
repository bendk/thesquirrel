# Generated by Django 2.2.16 on 2020-10-28 17:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import editor.fields
import events.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', editor.fields.EditorTextField()),
                ('location', models.CharField(max_length=255)),
                ('bottomliner', models.CharField(max_length=255)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
            ],
            bases=(models.Model, events.models.EventTimeMixin),
        ),
        migrations.CreateModel(
            name='SpaceUseRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('state', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('D', 'Declined'), ('C', 'Canceled')], default='P', max_length=1)),
                ('list', models.CharField(choices=[('I', 'Inbox'), ('W', 'Waiting for them'), ('N', 'Needs discussion'), ('M', 'Coming to meeting'), ('B', 'Needs bottomliner'), ('C', 'Complete')], default='I', max_length=1)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('deposit_paid', models.BooleanField(default=False)),
                ('has_bottomliner', models.BooleanField(default=False)),
                ('changed', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(db_index=True, max_length=255)),
                ('email', models.EmailField(db_index=True, max_length=255)),
                ('squirrel_member', models.CharField(blank=True, max_length=255)),
                ('organization', models.CharField(blank=True, max_length=255)),
                ('website', models.CharField(blank=True, max_length=255)),
                ('mission', models.TextField(blank=True)),
                ('phone_number', models.CharField(db_index=True, max_length=255)),
                ('additional_comments', models.TextField(blank=True)),
            ],
            options={
                'index_together': {('state', 'changed')},
            },
        ),
        migrations.CreateModel(
            name='OngoingSpaceUseRequest',
            fields=[
                ('spaceuserequest_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.SpaceUseRequest')),
                ('dates', models.CharField(max_length=255)),
                ('frequency', models.CharField(max_length=255)),
                ('squirrel_goals', models.TextField()),
                ('space_needs', models.CharField(max_length=255)),
            ],
            bases=('events.spaceuserequest',),
        ),
        migrations.CreateModel(
            name='SingleSpaceUseRequest',
            fields=[
                ('spaceuserequest_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='events.SpaceUseRequest')),
                ('event_type', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('setup_time', models.CharField(blank=True, max_length=255)),
                ('cleanup_time', models.CharField(blank=True, max_length=255)),
                ('event_charge', models.CharField(max_length=255)),
                ('squirrel_donation', models.TextField(blank=True)),
                ('number_of_people', models.CharField(max_length=255)),
                ('space_needs', models.TextField()),
            ],
            bases=('events.spaceuserequest',),
        ),
        migrations.CreateModel(
            name='SpaceUseNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('body', models.TextField()),
                ('space_use_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='events.SpaceUseRequest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['datetime'],
            },
        ),
        migrations.CreateModel(
            name='EventRepeatExclude',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='excludes', to='events.Event')),
            ],
        ),
        migrations.CreateModel(
            name='EventRepeat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('W', 'Every week'), ('2W', 'Every other week'), ('1M', 'First week of the month'), ('2M', 'Second week of the month'), ('3M', 'Third week of the month'), ('4M', 'Fourth week of the month'), ('LM', 'Last week of the month'), ('13M', '1st/3rd week of the month'), ('24M', '2nd/4th week of the month')], max_length=3)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('su', models.BooleanField(default=False)),
                ('mo', models.BooleanField(default=False)),
                ('tu', models.BooleanField(default=False)),
                ('we', models.BooleanField(default=False)),
                ('th', models.BooleanField(default=False)),
                ('fr', models.BooleanField(default=False)),
                ('sa', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repeat_set', to='events.Event')),
            ],
            bases=(models.Model, events.models.EventTimeMixin),
        ),
        migrations.AddField(
            model_name='event',
            name='space_request',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='events.SpaceUseRequest'),
        ),
        migrations.CreateModel(
            name='CalendarItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calendar_items', to='events.Event')),
            ],
            bases=(models.Model, events.models.EventTimeMixin),
        ),
    ]
