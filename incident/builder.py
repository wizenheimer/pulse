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

# TODO: Build Validators for choice fields


def build_policy_model(escalation_policy):
    """
    Creates and returns a new Escalation Policy Model
    """
    name = escalation_policy["policy"].get("name", "Untitled")
    delay = escalation_policy["policy"].get("delay", 10)
    repeat = escalation_policy["repeat"].get("repeat", 0)
    urgency = escalation_policy["urgency"].get("urgency", 1)
    impact = escalation_policy["impact"].get("impact", 1)

    # policy_id = EscalationPolicy.objects.create(name=name, delay=delay)
    return EscalationPolicy.objects.create(
        name=name,
        delay=delay,
        repeat=repeat,
        urgency=urgency,
        impact=impact,
    )

    # return EscalationPolicy.objects.get(id=policy_id)


def build_level_model(escalation_level):
    """
    Build a level model
    """
    name = escalation_level.get("name", "Unknown")
    delay = escalation_level.get("delay", 0)
    repeat = escalation_level.get("repeat", 0)
    urgency = escalation_level.get("urgency", 1)
    days = escalation_level.get("days", "1234567")
    timezone = escalation_level.get("timezone", "UTC")

    level = EscalationLevel.objects.create(
        name=name,
        delay_for=delay,
        repeat=repeat,
        days=days,
        urgency=urgency,
        end_time=end_time,
        timezone=timezone,
    )

    start_time = datetime.strptime(start_time, "%d:%m:%y %H:%M:%S")
    if start_time is not None:
        start_time = escalation_level.get("start_time", None)
        level.start_time = start_time

    end_time = escalation_level.get("end_time", None)
    if end_time is not None:
        end_time = datetime.strptime(end_time, "%d:%m:%y %H:%M:%S")
        level.end_time = end_time

    level.save()

    # return EscalationLevel.objects.get(id=level)
    return level


def build_action_model(action):
    """
    Build the action model
    """
    name = action.get("name", "Action")
    intent = action.get("intent", "Alert")
    context = action.get("context", "")
    entity = action.get("entity", "None")
    entity_type = action.get("type", "Attribute")

    action = EscalationAction.objects.create(
        name=name,
        intent=intent,
        context=context,
        entity=entity,
        entity_type=entity_type,
    )

    # return EscalationAction.get(id=action)
    return action


def build_model(url=None):
    # response = requests.get(url)

    # # raise an exception if the response is not OK
    # response.raise_for_status()

    # text = response.text
    # file = io.StringIO(text)

    # escalation_policy = yaml.safe_load(file)
    # for development purposes

    with open("incident/escalation policy/example.yaml", "r") as file:
        escalation_policy = yaml.safe_load(file)

    # Extract and print the name of the escalation policy
    policy_instance = build_policy_model(escalation_policy)

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

    return policy_instance.id
