from questfoundry.models import Artifact, HookCard, TUBrief


def test_artifact_creation():
    artifact = Artifact(type="test", data={})
    assert artifact.type == "test"

def test_hook_card():
    card = HookCard(data={"title": "Test"})
    assert card.type == "hook_card"

def test_tu_brief():
    brief = TUBrief(data={})
    assert brief.type == "tu_brief"
