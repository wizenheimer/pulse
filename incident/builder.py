import io
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
    delay = escalation_policy["policy"].get("delay", 0)

    # policy_id = EscalationPolicy.objects.create(name=name, delay=delay)
    return EscalationPolicy.objects.create(name=name, delay=delay)

    # return EscalationPolicy.objects.get(id=policy_id)


def build_level_model(escalation_level):
    """
    Build a level model
    """
    name = escalation_level.get("name", "Unknown")
    delay = escalation_level.get("delay", 0)
    repeat = escalation_level.get("repeat", 0)

    level_id = EscalationLevel.objects.create(
        name=name, delay_for=delay, repeat_for=repeat
    )

    # return EscalationLevel.objects.get(id=level_id)
    return level_id


def build_action_model(action):
    """
    Build the action model
    """
    name = action.get("name", "Action")
    system = action.get("system", "LOG")
    entity = action.get("entity", "None")
    entity_type = action.get("type", "Attribute")
    context = action.get("context", "")

    action_id = EscalationAction.objects.create(
        name=name,
        system=system,
        entity=entity,
        context=context,
        entity_type=entity_type,
    )

    # return EscalationAction.get(id=action_id)
    return action_id


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
