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
                    temp = handle_person_in_unknown_format(project[field2])
                    if isinstance(temp, dict) and len(temp.keys()) > 0:
                        temp["@type"] = "Person"
                        ret_data[field1] = temp
                    elif isinstance(temp, list):
                        if len(temp) > 1:
                            for person in temp:
                                person["@type"] = "Person"
                            ret_data[field1] = temp
                        elif len(temp) == 1:
                            temp[0]["@type"] = "Person"
                            ret_data[field1] = temp[0]
                else:
                    ret_data[field1] = project[field2]

    poetry = data.get("tool.poetry")
    if not poetry is None:
        if not project is None:
            raise ValueError("Both project and tool.poetry table exist.")
        for (field1, field2) in field_to_property_mapping_in_poetry:
            if not poetry.get(field2) is None:
                if field1 in ["author", "maintainer"]:
                    temp = handle_person_in_unknown_format(poetry[field2])
                    if isinstance(temp, dict) and len(temp.keys()) > 0:
                        ret_data[field1] = temp
                    elif isinstance(temp, list):
                        if len(temp) > 1:
                            ret_data[field1] = temp
                        elif len(temp) == 1:
                            ret_data[field1] = temp[0]
                else:
                    ret_data[field1] = poetry[field2]

    return ret_data

def handle_person_in_unknown_format(persons):
    if isinstance(persons, list):
        return_list = []
        for person in persons:
            if isinstance(person, dict):
                temp = remove_forbidden_keys(person)
                if len(temp.keys()) > 0:
                    return_list.append(temp)
            else:
                raise ValueError("A person must be a dict.")
        return return_list
    if isinstance(persons, dict):
        return remove_forbidden_keys(persons)
    raise ValueError("A person must be a dict.")

def remove_forbidden_keys(person):
    allowed_keys = ["givenName", "lastName", "email", "@id", "@type"]
    keys = list(person.keys())
    for key in keys:
        if not key in allowed_keys:
            del person[key]
    return person
