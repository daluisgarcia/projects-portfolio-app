import django.db.models.deletion
import pgvector.django
from django.db import migrations, models


class Migration(migrations.Migration):
    """Add the BlogPostEmbedding model for storing vector embeddings of blog posts.

    Two operations:

    1. ``VectorExtension()`` — enables the ``vector`` extension in PostgreSQL.
       Skipped automatically on non-postgres backends (the underlying
       ``CreateExtension`` operation bails out when ``connection.vendor``
       is not ``"postgresql"``).
    2. ``CreateModel`` for ``BlogPostEmbedding`` — ``ForeignKey`` to ``BlogPost``
       (CASCADE delete, ``related_name="embeddings"``), a 384-dim ``VectorField``
       for the embedding, and a ``model_name`` char field for the embedding
       model identifier. ``unique_together = (post, model_name)`` allows storing
       embeddings from multiple models per post.
    """

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        pgvector.django.VectorExtension(),
        migrations.CreateModel(
            name="BlogPostEmbedding",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("embedding", pgvector.django.VectorField(dimensions=384)),
                (
                    "model_name",
                    models.CharField(default="all-MiniLM-L6-v2", max_length=100),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="embeddings",
                        to="blog.blogpost",
                    ),
                ),
            ],
            options={
                "verbose_name": "Blog Post Embedding",
                "verbose_name_plural": "Blog Post Embeddings",
                "ordering": ("post", "model_name"),
                "unique_together": {("post", "model_name")},
            },
        ),
    ]
