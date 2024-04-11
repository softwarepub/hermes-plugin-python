import logging

from hermes.commands.harvest.base import HermesHarvestPlugin
from pydantic import BaseModel

from hermes_git.util.git_contributor_data import ContributorData
from hermes_git.util.git_node_register import NodeRegister

class GitHarvestSettings(BaseModel):
    from_branch: str = 'main'


class GitHarvestPlugin(HermesHarvestPlugin):
    settings_class = GitHarvestSettings

    def __call__(self, command):
        print("Hello World!")

        return {}, {}

    def _audit_contributors(self, contributors, audit_log: logging.Logger):
        # Collect all authors that have ambiguous data
        unmapped_contributors = [a for a in contributors._all if len(a.email) > 1 or len(a.name) > 1]

        if unmapped_contributors:
            # Report to the audit about our findings
            audit_log.warning('!!! warning "You have unmapped contributors in your Git history."')
            for contributor in unmapped_contributors:
                if len(contributor.email) > 1:
                    audit_log.info("    - %s has alternate email: %s", str(contributor),
                                   ', '.join(contributor.email[1:]))
                if len(contributor.name) > 1:
                    audit_log.info("    - %s has alternate names: %s", str(contributor),
                                   ', '.join(contributor.name[1:]))
            audit_log.warning('')

            audit_log.info(
                "Please consider adding a `.maillog` file to your repository to disambiguate these contributors.")
            audit_log.info('')
            audit_log.info('``` .mailmap')

            audit_log.info('```')

    def _merge_contributors(self, git_authors: NodeRegister, git_committers: NodeRegister) -> NodeRegister:
        """
        Merges the git authors and git committers :py:class:`NodeRegister` and assign the respective roles for each node.
        """
        git_contributors = NodeRegister(ContributorData, 'email', 'name', email=str.upper)
        for author in git_authors._all:
            git_contributors.update(email=author.email[0], name=author.name[0], timestamp=author.timestamp,
                                    role='git author')

        for committer in git_committers._all:
            git_contributors.update(email=committer.email[0], name=committer.name[0], timestamp=committer.timestamp,
                                    role='git committer')

        return git_contributors