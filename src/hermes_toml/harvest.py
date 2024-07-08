import os
import pathlib
import toml

from pydantic import BaseModel

from hermes.commands.harvest.base import HermesHarvestCommand, HermesHarvestPlugin

class TomlHarvestSettings(BaseModel):
    """Settings class for this plugin"""
    filename: str = 'pyproject.toml'


class TomlHarvestPlugin(HermesHarvestPlugin):
    """Base class for the hermes plugin that harvests .toml files"""

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
        #set the working directory to the correct location
        path = command.args.path
        old_path = pathlib.Path.cwd()
        if path != old_path:
            os.chdir(path)

        #harvesting the data from the .toml file specified in the Settings class
        data = self.read_from_toml(command.settings.toml.filename)

        #resetting the working directory
        if path != old_path:
            os.chdir(old_path)

        #returning the harvested data and some metadata
        return data, {"filename": command.settings.toml.filename}

    @classmethod
    def read_from_toml(cls, file):
        #load the toml file as a dictionary
        data  = toml.load(file)

        ret_data = {}

        #iterate over each table
        #read it's information and store it according to the mapping
        #if more than one table existis raise an error as
        #the information could be overlapping and there should only be one table
        for table, mapping in cls.table_with_mapping.items():
            table = data.get(table)
            if not table is None:
                if len(ret_data.keys()) != 0:
                    raise ValueError("Both project and tool.poetry table exist.")
                #read the data from the table
                ret_data = cls.read_from_one_table(table, mapping)

        #return the result
        return ret_data

    @classmethod
    def read_from_one_table(cls, table, mapping):
        ret_data = {}

        #iterate over each mapping
        for (field1, field2) in mapping:
            if not table.get(field2) is None:
                #if this field exists
                #some cases need additional processing
                if field2 == "requires-python":
                    #add python to the python version number for the runtime platform
                    ret_data[field1] = "Python " + table[field2]

                elif field1 in ["author", "maintainer"]:
                    #the integrity of the format of the person(s) is assured
                    persons = cls.handle_person_in_unknown_format(table[field2])

                    #store the (corrected) format of the person(s) data
                    persons = cls.handle_differnt_possibilities_for_persons(persons)
                    if not persons is None:
                        ret_data[field1] = persons

                else:
                    #add the data of a field that needs no processing
                    ret_data[field1] = table[field2]

            else:
                #if it doesn't exist
                continue

        #return the important data of the table
        return ret_data

    @classmethod
    def handle_differnt_possibilities_for_persons(cls, persons):
        #check if it is one person in the right format or none
        if isinstance(persons, dict):
            if len(persons.keys()) > 0:
                #add the @type field
                persons["@type"] = "Person"

            else:
                #set to None if there is no persons data to store
                persons = None

        #check if how many persons are in the list
        elif isinstance(persons, list):
            if len(persons) > 1:
                #add for every person the @type field
                for person in persons:
                    person["@type"] = "Person"

            elif len(persons) == 1:
                #add the @type field
                persons[0]["@type"] = "Person"

                #remove the list as it is only one peron inside
                persons = persons[0]

            else:
                #set to None if there is no persons data to store
                persons = None

        #return the persons in the (corrected) format
        return persons

    @classmethod
    def handle_person_in_unknown_format(cls, persons):
        #check wheter it is one or are more persons
        if isinstance(persons, list):
            #in case of potentially at least two persons
            return_list = []
            #for each person
            for person in persons:

                #check if the datatype is correct
                if isinstance(person, dict):
                    #remove all attributes that aren't allowed
                    temp = cls.remove_forbidden_keys(person)
                    #if this leads to the dataset losing all values don't add it to the return list
                    if len(temp.keys()) > 0:
                        return_list.append(temp)

                else:
                    #if the person isn't a dictionary raise an Error
                    raise ValueError("A person must be a dict.")

            #return the person(s)
            return return_list

        #if it is only one or no person
        #check for the right datatype
        if isinstance(persons, dict):
            #if it is correct return the person with all forbidden keys
            #the 'person' may be an empty dictionary if all keys are incorrect
            return cls.remove_forbidden_keys(persons)

        #raise an error if the persons data is not in the right format
        raise ValueError("A person must be a dict.")

    @classmethod
    def remove_forbidden_keys(cls, person):
        #the keys are extracted as the dictionary may be resized
        keys = list(person.keys())

        #check for every key if it is allowed and if not remove it
        for key in keys:
            if not key in cls.allowed_keys_for_person:
                del person[key]

        #return the persons data
        return person
