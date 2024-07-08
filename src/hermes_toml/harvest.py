import os
import pathlib
import toml

from pydantic import BaseModel

from hermes.commands.harvest.base import HermesHarvestCommand, HermesHarvestPlugin

class TomlHarvestSettings(BaseModel):
    filename: str = 'pyproject.toml'


class TomlHarvestPlugin(HermesHarvestPlugin):
    settings_class = TomlHarvestSettings
    table_with_mapping = {
        "project": [
            ("name", "name"), ("version", "version"), ("description", "description"),
            ("runtimePlatform", "requires-python"), ("author", "authors"),
            ("maintainer", "maintainers"), ("keywords", "keywords")
        ],
        "tool.poetry": [
            ("name", "name"), ("version", "version"), ("description", "description"),
            ("author", "authors"), ("maintainer", "maintainers"), ("url", "homepage"),
            ("codeRepository", "repository"), ("keywords", "keywords")
        ]
    }
    allowed_keys_for_person = ["givenName", "lastName", "email", "@id", "@type"]

    def __call__(self, command: HermesHarvestCommand):
        path = command.args.path
        old_path = pathlib.Path.cwd()
        if path != old_path:
            os.chdir(path)

        data = self.read_from_toml(command.settings.toml.filename)

        if path != old_path:
            os.chdir(old_path)

        return data, {"filename": command.settings.toml.filename}

    @classmethod
    def read_from_toml(cls, file):
        data  = toml.load(file)
        ret_data = {}
        for table, mapping in cls.table_with_mapping.items():
            table = data.get(table)
            if not table is None:
                if len(ret_data.keys()) != 0:
                    raise ValueError("Both project and tool.poetry table exist.")
                ret_data = cls.read_from_one_table(table, mapping)

        return ret_data

    @classmethod
    def read_from_one_table(cls, table, mapping):
        ret_data = {}
        for (field1, field2) in mapping:
                if not table.get(field2) is None:
                    if field2 == "requires-python":
                        ret_data[field1] = "Python " + table[field2]
                    elif field1 in ["author", "maintainer"]:
                        temp = cls.handle_person_in_unknown_format(table[field2])
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
                        ret_data[field1] = table[field2]
        return ret_data

    @classmethod
    def handle_person_in_unknown_format(cls, persons):
        if isinstance(persons, list):
            return_list = []
            for person in persons:
                if isinstance(person, dict):
                    temp = cls.remove_forbidden_keys(person)
                    if len(temp.keys()) > 0:
                        return_list.append(temp)
                else:
                    raise ValueError("A person must be a dict.")
            return return_list
        if isinstance(persons, dict):
            return cls.remove_forbidden_keys(persons)
        raise ValueError("A person must be a dict.")

    @classmethod
    def remove_forbidden_keys(cls, person):
        keys = list(person.keys())
        for key in keys:
            if not key in cls.allowed_keys_for_person:
                del person[key]
        return person
