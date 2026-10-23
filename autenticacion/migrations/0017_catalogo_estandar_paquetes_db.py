from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('autenticacion', '0016_mej003_estandar_paquetes'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstandarPaquete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clave', models.SlugField(max_length=40, unique=True)),
                ('version', models.CharField(max_length=20)),
                ('nombre', models.CharField(max_length=180)),
                ('proposito', models.TextField()),
                ('activo', models.BooleanField(default=True)),
                ('actualizado_en', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Estándar de paquetes',
                'verbose_name_plural': 'Estándares de paquetes',
                'ordering': ['clave'],
            },
        ),
        migrations.CreateModel(
            name='FuenteEstandarPaquete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.SlugField(max_length=60)),
                ('titulo', models.CharField(max_length=180)),
                ('entidad', models.CharField(max_length=180)),
                ('alcance', models.TextField()),
                ('url', models.URLField(blank=True, max_length=500)),
                ('verificada', models.BooleanField(default=False)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('activa', models.BooleanField(default=True)),
                ('estandar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fuentes', to='autenticacion.estandarpaquete')),
            ],
            options={
                'verbose_name': 'Fuente del estándar',
                'verbose_name_plural': 'Fuentes del estándar',
                'ordering': ['orden', 'titulo'],
            },
        ),
        migrations.CreateModel(
            name='ModalidadTurismo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.SlugField(max_length=40)),
                ('nombre', models.CharField(max_length=120)),
                ('descripcion', models.TextField(blank=True)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('activa', models.BooleanField(default=True)),
                ('estandar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modalidades', to='autenticacion.estandarpaquete')),
            ],
            options={
                'verbose_name': 'Modalidad de turismo',
                'verbose_name_plural': 'Modalidades de turismo',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='PrincipioEstandarPaquete',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.SlugField(max_length=50)),
                ('descripcion', models.TextField()),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('activo', models.BooleanField(default=True)),
                ('estandar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='principios', to='autenticacion.estandarpaquete')),
            ],
            options={
                'verbose_name': 'Principio del estándar',
                'verbose_name_plural': 'Principios del estándar',
                'ordering': ['orden', 'id'],
            },
        ),
        migrations.AddConstraint(
            model_name='fuenteestandarpaquete',
            constraint=models.UniqueConstraint(fields=('estandar', 'codigo'), name='fuente_codigo_unico_por_estandar'),
        ),
        migrations.AddConstraint(
            model_name='modalidadturismo',
            constraint=models.UniqueConstraint(fields=('estandar', 'codigo'), name='modalidad_codigo_unico_por_estandar'),
        ),
        migrations.AddConstraint(
            model_name='principioestandarpaquete',
            constraint=models.UniqueConstraint(fields=('estandar', 'codigo'), name='principio_codigo_unico_por_estandar'),
        ),
    ]
