# Generated by Django 2.2.4 on 2020-02-07 15:26

from django.db import migrations, transaction

BATCH_SIZE = 5000


def populate_template_deps(apps, schema_editor):  # pragma: no cover
    Flow = apps.get_model("flows", "Flow")
    Template = apps.get_model("templates", "Template")

    num_updated = 0
    max_id = -1
    while True:
        batch = list(
            Flow.objects.filter(id__gt=max_id, is_active=True)
            .only("id", "org_id", "metadata")
            .order_by("id")[:BATCH_SIZE]
        )
        if not batch:
            break

        with transaction.atomic():
            for flow in batch:
                dependencies = flow.metadata.get("dependencies", [])
                template_uuids = [d["uuid"] for d in dependencies if d["type"] == "template"]
                if not template_uuids:
                    continue

                templates = Template.objects.filter(org_id=flow.org_id, uuid__in=template_uuids)

                flow.template_dependencies.clear()
                flow.template_dependencies.add(*templates)

        num_updated += len(batch)
        print(f" > Updated {num_updated} flows with template dependencies")

        max_id = batch[-1].id


def reverse(apps, schema_editor):  # pragma: no cover
    pass


def apply_manual():  # pragma: no cover
    from django.apps import apps

    populate_template_deps(apps, None)


class Migration(migrations.Migration):

    dependencies = [("flows", "0224_flow_dependencies")]

    operations = [migrations.RunPython(populate_template_deps, reverse)]
