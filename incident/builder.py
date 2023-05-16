import io
import datetime
import yaml
import requests
from .models import (
    EscalationAction,
    EscalationLevelAssignment,
    EscalationPolicy,
    EscalationLevel,
)
from django.core.exceptions import ValidationError
from incident.models import Webhook
from users.models import User, UserGroups
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

# TODO: Build Validators for choice fields
# TODO: Build Validator for YAML validation
# TODO: Build Transform functions for all caps and trim spaces for types


def build_policy_model(escalation_policy):
    """
    Creates and returns a new Escalation Policy Model
    """
    name = escalation_policy.get("name", "My Escalation Policy")
    return EscalationPolicy.objects.create(name=name)


def build_level_model(escalation_level):
    """
    Build a level model
    """
    name = escalation_level.get("name", "MyLevel")
    return EscalationLevel.objects.create(name=name)


def build_action_model(action):
    """
    Build the action model
    """
    name = action.get("name", "MyAction")
    entity = action.get("entity", None)
    entity_type = action.get("type", None)

    if entity_type is None or entity is None:
        raise ValidationError("entity type and entity must be specified")

    entity_type = entity_type.upper()
    entity = int(entity)

    action = None

    # TODO: handle target_object_validation
    if entity_type == "ID":
        action = EscalationAction.objects.create(
            name=name,
            entity_type=ContentType.objects.get_for_model(User),
            target_object_id=entity,
        )
    elif entity_type == "GROUP":
        action = EscalationAction.objects.create(
            name=name,
            entity_type=ContentType.objects.get_for_model(UserGroups),
            target_object_id=entity,
        )
    elif entity_type == "HOOK":
        action = EscalationAction.objects.create(
            name=name,
            entity_type=ContentType.objects.get_for_model(Webhook),
            target_object_id=entity,
        )

    if action is None:
        raise ValidationError("Entity type isn't valid")

    return action


def build_model(
    policy_id=None,
    url=None,
    notify_all=False,
):
    policy_instance = None
    escalation_policy = None

    # for development purposes
    if settings.DEBUG:
        with open("incident/escalation policy/example.yaml", "r") as file:
            escalation_policy = yaml.safe_load(file)
            policy_instance = build_policy_model(escalation_policy)
            policy_instance.source = file
    elif policy_id is not None:
        policy_instance = EscalationPolicy.objects.get(id=policy_id)
        escalation_policy = policy_instance.source
    elif url is not None:
        response = requests.get(url)
        response.raise_for_status()
        text = response.text
        file = io.StringIO(text)
        escalation_policy = yaml.safe_load(file)
        policy_instance = build_policy_model(escalation_policy)
        policy_instance.source = file

    level_position = 0
    # Iterate over the levels of the escalation policy
    for level in escalation_policy["policy"]["levels"]:
        level_position += 1
        level_instance = build_level_model(level)

        level_assignment = EscalationLevelAssignment(
            level=level_instance, policy=policy_instance
        )
        level_assignment.level_number = level_position
        level_assignment.save()

        # Iterate over the actions of the level
        for action in level.get("actions", []):
            build_action_model(action)
            
    # indicate the max level
    policy_instance.max_level = level_position
    policy_instance.notify_all = notify_all
    policy_instance.save()
    return policy_instance
