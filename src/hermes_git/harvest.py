import logging
import os
import pathlib
import toml

from pydantic import BaseModel
import shutil

from hermes.commands.harvest.base import HermesHarvestCommand, HermesHarvestPlugin

class GitHarvestSettings(BaseModel):
    from_branch: str = 'HEAD'


class GitHarvestPlugin(HermesHarvestPlugin):
    settings_class = GitHarvestSettings

    #def __init__(self):
    #    self.git_exe = shutil.which('git')
    #    if not self.git_exe:
    #        raise RuntimeError('Git not available!')

    def __call__(self, command: HermesHarvestCommand):
        path = command.args.path
        old_path = pathlib.Path.cwd()
        if path != old_path:
            os.chdir(path)

        toml_file_list = []
        for file in os.listdir():
            if os.path.isfile(file) and file[-5:] == ".toml":
                if file[-11:] == "hermes.toml":
                    continue
                toml_file_list.append(file)

        data = dict()
        for file in toml_file_list:
            data.update(read_from_toml(file))

        return data, dict()

def read_from_toml(file):
    data  = toml.load(file)
    ret_data = dict()
    field_to_property_mapping_in_project = [
        ("name", "name"), ("version", "version"), ("description", "description"),
        ("runtimePlatform", "requires-python"), ("author", "authors"), 
        ("maintainer", "maintainers"), ("keywords", "keywords")
    ]
    field_to_property_mapping_in_poetry = [
        ("name", "name"), ("version", "version"), ("description", "description"),
        ("author", "authors"), ("maintainer", "maintainers"), ("url", "homepage"),
        ("codeRepository", "repository"), ("keywords", "keywords")
    ]
    project = data.get("project")
    if not project is None:
        for (field1, field2) in field_to_property_mapping_in_project:
            if not project.get(field2) is None:
                if field2 == "requires-python":
                    ret_data[field1] = "Python " + project[field2]
                else:
                    ret_data[field1] = project[field2]
                if field1 in ["author", "maintainer"]:
                    if isinstance(ret_data[field1], list):
                        for item in ret_data[field1]:
                            if isinstance(item, str):
                                raise ValueError("Person is not a string")
                            item["@type"] = "Person"
                    else:
                        if isinstance(ret_data[field1], str):
                            raise ValueError("Person is not a string")
                        ret_data[field1]["@type"] = "Person"

    poetry = data.get("tool.poetry")
    if not poetry is None:
        for (field1, field2) in field_to_property_mapping_in_poetry:
            if not poetry.get(field2) is None:
                ret_data[field1] = poetry[field2]
    return ret_data
