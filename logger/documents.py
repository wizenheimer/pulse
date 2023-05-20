from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.contrib.contenttypes.models import ContentType
from logger.models import Log


@registry.register_document
class LogDocument(Document):
    status = fields.TextField(
        attr="status",
        fields={
            "raw": fields.TextField(),
        },
    )
    response_time = fields.Double()
    message = fields.TextField(
        attr="message",
        fields={
            "raw": fields.TextField(),
        },
    )
    response_body = fields.TextField(
        attr="response_body",
        fields={
            "raw": fields.TextField(),
        },
    )
    target = fields.Nested(
        properties={
            "model_name": fields.Keyword(),
            "id": fields.Keyword(),
            # Add other fields
        }
    )

    def prepare_target(self, instance):
        target = instance.target

        if target:
            model_name = ContentType.objects.get_for_model(target).model

            return {
                "model_name": model_name,
                "id": str(target.id),
                "name": target.name,
                # Map other fields from the related models
            }

        return None

    class Index:
        name = "logs"

    class Django:
        model = Log
