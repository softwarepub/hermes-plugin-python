import os
import pathlib
import toml

from pydantic import BaseModel

from hermes.commands.harvest.base import HermesHarvestCommand, HermesHarvestPlugin

class TomlHarvestSettings(BaseModel):
    filename: str = 'pyproject.toml'


class TomlHarvestPlugin(HermesHarvestPlugin):
    settings_class = TomlHarvestSettings

    def __call__(self, command: HermesHarvestCommand):
        path = command.args.path
        old_path = pathlib.Path.cwd()
        if path != old_path:
            os.chdir(path)

        data = read_from_toml(command.settings.toml.filename)

        return data, {}

def read_from_toml(file):
    data  = toml.load(file)
    ret_data = {}
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
                elif field1 in ["author", "maintainer"]:
                    ret_data[field1] = handle_person_in_unknown_format(project[field2])
                else:
                    ret_data[field1] = project[field2]

    poetry = data.get("tool.poetry")
    if not poetry is None:
        for (field1, field2) in field_to_property_mapping_in_poetry:
            if not poetry.get(field2) is None:
                ret_data[field1] = poetry[field2]

    return ret_data

def handle_person_in_unknown_format(persons):
    if isinstance(persons, list):
        return_list = []
        for person in persons:
            if isinstance(person, dict):
                if check_if_correct_keys(person):
                    return_list.append(person)
            else:
                raise ValueError("A person must be a dict.")
        return return_list
    if isinstance(persons, dict):
        if check_if_correct_keys(persons):
            return persons
    else:
        raise ValueError("A person must be a dict.")

def check_if_correct_keys(person):
    allowed_keys = ["givenName", "lastName", "email", "@id"]
    for key in person.keys():
        if not key in allowed_keys:
            raise ValueError(f"{key} is not allowed for a person.")
    return True
