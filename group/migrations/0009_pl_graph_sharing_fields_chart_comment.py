from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0008_grouptimeline_grouptimelinecomment_replycomment'),
        ('member', '0003_plants_planttag_sensordata_soiltag_users_room_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pl_graph_sharing',
            name='start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pl_graph_sharing',
            name='end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pl_graph_sharing',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='PlGraphSharingComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=1500)),
                ('pictures', models.ImageField(blank=True, null=True, upload_to='chart_comment_pictures/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('chart_sharing_fk', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='group.pl_graph_sharing'
                )),
                ('commenter_fk', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='member.person'
                )),
            ],
            options={
                'db_table': 'plgraphsharingcomment',
            },
        ),
    ]