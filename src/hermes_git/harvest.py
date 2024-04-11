from hermes.commands.harvest.base import HermesHarvestPlugin
from pydantic import BaseModel


class GitHarvestSettings(BaseModel):
    from_branch: str = 'main'


class GitHarvestPlugin(HermesHarvestPlugin):
    settings_class = GitHarvestSettings

    def __call__(self, command):
        print("Hello World!")

        return {}, {}
