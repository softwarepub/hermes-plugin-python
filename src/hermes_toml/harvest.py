# SPDX-FileCopyrightText: 2024 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileContributor: Michael Meinel
# SPDX-FileContributor: Michael Fritzsche

"""A hermes harvest plugin that harvests the .toml file of the project"""

from os import chdir, getcwd
from email.utils import getaddresses

import re
import toml
from pydantic import BaseModel
# from hermes.model import SoftwareMetadata
from hermes.commands.harvest.base import HermesHarvestCommand, HermesHarvestPlugin


class TomlHarvestSettings(BaseModel):
    """
    Settings class for this plugin
    """

    filename: str = 'pyproject.toml'


class TomlHarvestPlugin(HermesHarvestPlugin):
    """
    Base class for the hermes plugin that harvests .toml files
    """

    settings_class = TomlHarvestSettings
    easy_mappings = {
        "project": {
            "name": "schema:name", "version": "schema:version", "description": "schema:description",
            "keywords": "schema:keywords"
        },
        "poetry": {
            "name": "schema:name", "version": "schema:version", "description": "schema:description",
            "keywords": "schema:keywords", "repository": "schema:CodeRepository"
        },
        "flit": {
            "keywords": "schema:keywords", "dist-name": "schema:name",
            "module": "schema:alternateName"
        }
    }

    def __call__(self, command: HermesHarvestCommand):
        """
        start of the process of harvesting the .toml file
        invoked when hermes harvest is run and this module is registered as a harvester
        """

        # set the working directory temporary to the correct location
        old_dir = getcwd()
        chdir(command.args.path)

        # harvesting the data from the .toml file specified in the Settings class
        data = {}  # SoftwareMetadata()
        self.read_from_toml(command.settings.toml.filename, data)

        chdir(old_dir)

        # returning the harvested data and some metadata
        return data, {"filename": command.settings.toml.filename}

    @classmethod
    def read_from_toml(cls, file, data):
        """
        Open the given .toml file and write its contents in the correct JSON-LD format into the
        given SoftwareMetadata object.
        Harvests the data which is in the tables of the most common buildtools or the project table.

        Parameter
        ---------
        file:
            The path to the .toml file to be harvested.
        data:
            The SoftwareMetadata object the data is to be written to

        Returns
        -------
        None

        Raises
        ------
        Nothing
        """

        # load the toml file as a dictionary
        try:
            if not isinstance(toml_data := toml.load(file), dict):
                return
        except Exception as exc:
            raise type(exc)(f"Something went wrong while reading the given file {file}") from exc

        # harvest project table
        project_data = toml_data.get("project")
        if isinstance(project_data, dict):
            cls.handle_project_table(project_data, data)

        if not isinstance(tool_table := toml_data.get("tool"), dict):
            return

        # harvest tool.poetry table
        poetry_data = tool_table.get("poetry")
        if isinstance(poetry_data, dict):
            cls.handle_poetry_table(poetry_data, data)

        # harvest tool.flit.metadata table
        flit_data = tool_table.get("flit")
        if isinstance(flit_data, dict) and isinstance(flit_data := flit_data.get("metadata"), dict):
            cls.handle_flit_table(flit_data, data)

    @classmethod
    def handle_project_table(cls, table: dict, data):
        """
        Extract all metadata from the given table assuming it follows the PEP standard into the
        given SoftwareMetadata object.

        Parameter
        ---------
        table: dict
            The content of the project table of the pyproject.toml following the PEP standard in a
            python dictionary.
        data: SoftwareMetadata
            The SoftwareMetadata object the extracted data is to be written to.

        Returns
        -------
        None

        Raises
        ------
        Nothing
        """

        # handle all easy mappings
        for key, dest_key in cls.easy_mappings.get("project").items():
            if (value := table.get(key, None)) is None:
                continue
            if (isinstance(value, str) or isinstance(value, list) and all(isinstance(val, str) for val in value)):
                data[dest_key] = value

        # check authors
        if not (authors := table.get("authors")) is None:
            cls.handle_person(authors, "schema:author", data)

        # check maintainer
        if not (maintainer := table.get("maintainers")) is None:
            cls.handle_person(maintainer, "schema:maintainer", data)

        # check urls
        if not (urls := table.get("urls")) is None:
            cls.handle_urls(urls, data)

        # check classifiers
        if not (classifiers := table.get("classifiers")) is None:
            cls.handle_pypi_classifieres(classifiers, data)

    @classmethod
    def handle_poetry_table(cls, table: dict, data):
        """
        Extract all metadata from the given table assuming it follows the deprecated standard of
        poetry into the given SoftwareMetadata object.

        Parameter
        ---------
        table: dict
            The content of the project table of the pyproject.toml following the deprecated standard
            of poetry in a python dictionary.
        data: SoftwareMetadata
            The SoftwareMetadata object the extracted data is to be written to.

        Returns
        -------
        None

        Raises
        ------
        Nothing
        """

        # handle all easy mappings
        for key, dest_key in cls.easy_mappings.get("poetry").items():
            if (value := table.get(key, None)) is None:
                continue
            if (isinstance(value, str) or isinstance(value, list) and all(isinstance(val, str) for val in value)):
                data[dest_key] = value

        # check authors
        if not (authors := table.get("authors")) is None:
            cls.handle_person(authors, "schema:author", data)

        # check maintainer
        if not (maintainer := table.get("maintainers")) is None:
            cls.handle_person(maintainer, "schema:maintainer", data)

        # check urls
        if not (urls := table.get("urls")) is None:
            cls.handle_urls(urls, data)

        # check classifiers
        if not (classifiers := table.get("classifiers")) is None:
            cls.handle_pypi_classifieres(classifiers, data)

    @classmethod
    def handle_flit_table(cls, table: dict, data):
        """
        Extract all metadata from the given table assuming it follows the deprecated standard of
        flit into the given SoftwareMetadata object.

        Parameter
        ---------
        table: dict
            The content of the project table of the pyproject.toml following the deprecated standard
            of flit in a python dictionary.
        data: SoftwareMetadata
            The SoftwareMetadata object the extracted data is to be written to.

        Returns
        -------
        None

        Raises
        ------
        Nothing
        """

        # handle all easy mappings
        for key, dest_key in cls.easy_mappings.get("flit").items():
            if (value := table.get(key, None)) is None:
                continue
            if isinstance(value, str) and value != "":
                data[dest_key] = value
            elif isinstance(value, list) and len(value) != 0:
                value = list(set([val for val in value if isinstance(val, str) and val != ""]))
                if len(value) == 0:
                    continue
                if len(value) == 1:
                    value = value[0]
                data[dest_key] = value

        # check author
        possible_author = {"name": table.get("author", ""), "email": table.get("author-email", "")}
        cls.handle_person(possible_author, "schema:author", data)

        # check maintainer
        possible_maintainer = {"name": table.get("maintainer", ""),
                               "email": table.get("maintainer-email", "")}
        cls.handle_person(possible_maintainer, "schema:maintainer", data)

        # check classifiers
        if not (classifiers := table.get("classifiers")) is None:
            cls.handle_pypi_classifieres(classifiers, data)

    @classmethod
    def handle_person(cls, person_data, key: str, data):
        """
        Handle one or multiple persons. Extract their email and name and then store it in the
        provided SoftwareMetadata object with the given key.

        Parameter
        ---------
        person_data: Any
            The data in the raw format of one or multiple persons.
        key: str
            The key for storing the results in the SoftwareMetadata object.
        data: SoftwareMetadata
            The SoftwareMetadata object the data is to be stored in.

        Returns
        -------
        None

        Raises
        ------
        Nothing
        """
        if not isinstance(key, str) or len(key) == 0:
            return

        if isinstance(person_data, list):
            # try to extract the name and email from all persons in the list
            # and add the resulting list as a list or a single item to the SoftwareMetadata object
            persons = []
            for person in person_data:
                # check if person contains data and store it in the correct format
                if not (person := cls.extract_personal_data(person)) == {}:
                    persons.append(person)
            if len(persons) > 1:
                data[key] = persons
            elif len(persons) == 1:
                data[key] = persons[0]
        elif not (person := cls.extract_personal_data(person_data)) == {}:
            # add the persons data to the SoftwareMetadata object
            data[key] = person

    @classmethod
    def extract_personal_data(cls, person) -> dict[str, str]:
        """
        Extract an email address and a name from the given data in an unknown format that may
        represent a person.
        Recognized formats are a dict with keys name and email or a string ('name <email>').
        If no data can be extracted return an empty dictionary else one with the keys name and email
        and @type for valid JSON-LD but only if at least one of name and email are not empty.

        Parameter
        ---------
        person: Any
            The data of the potentiell person in an unknown format.

        Returns
        -------
        dict[str, str]
            An empty dictionary if no name and email could be extracted and one containg the keys
            name, email and type but only those contain a value.

        Raises
        ------
        Nothing
        """

        if not isinstance(person, (str, dict)):
            return {}
        # retrieve the name and email from the string or dict
        if isinstance(person, str):
            if person.find("@") != -1:
                [(name, email)] = getaddresses([person])
            else:
                name, email = (person, "")
        else:
            name, email = person.get("name", ""), person.get("email", "")
            if not isinstance(name, str):
                name = ""
            if not isinstance(email, str):
                email = ""

        # create an object with name, email and @type if name or email is not empty
        person = {}
        if name != "":
            person["schema:name"] = name
        # try to validate the email address
        if re.fullmatch(r"([a-z]|[A-Z]|[0-9])+(\.([a-z]|[A-Z]|[0-9])+)*@([a-z]|[A-Z]|[0-9])+"
                        r"\.([a-z]|[A-Z]|[0-9])+(\.([a-z]|[A-Z]|[0-9])+)*", email):
            person["schema:email"] = email
        if not person:
            return {}
        person["@type"] = "schema:Person"
        return person

    @classmethod
    def handle_pypi_classifieres(cls, classifiers: str | list[str], data):
        """
        Add the given pypi classifiers to the given SoftwareMetadata object using the correct keys.

        Parameter
        ---------
        classifiers: str |list[str]
            The classifier or the list of multiple (as specified by pypi).
        data: SoftwareMetadata
            The SoftwareMetadata object in which the classifiers are to be stored.

        Returns
        -------
        None

        Raises
        ------
        Nothing
        """

        if not isinstance(classifiers, (str, list)):
            return
        if isinstance(classifiers, str):
            classifiers = [classifiers]

        # remove duplicates
        classifiers = list(set(classifiers))

        sorted_classifiers = {
            "schema:targetProduct": [], "schema:audience": [], "schema:license": [],
            "schema:inLanguage": [], "schema:programming Language": [], "schema:about": []
        }
        # iterate over all classifiers and put them into the correct buckets
        for classifier in classifiers:
            if not isinstance(classifier, str):
                continue
            classifier = classifier.split(" :: ")
            if len(classifier) < 2:
                continue
            if (classifier[0] == "Operating System" and not (len(classifier) == 2 and classifier[1] == "Microsoft")):
                temp = {"@type": "schema:SoftwareApplication", "schema:name": classifier[-1]}
                sorted_classifiers["schema:targetProduct"].append(temp)
            elif classifier[0] == "Intended Audience":
                temp = {"@type": "schema:Audience", "schema:name": classifier[-1]}
                sorted_classifiers["schema:audience"].append(temp)
            elif (classifier[0] == "License" and not (classifier[1] == "OSI Approved" and len(classifier) == 2)):
                temp = {"@type": "schema:CreativeWork", "schema:name": classifier[-1]}
                sorted_classifiers["schema:license"].append(temp)
            elif classifier[0] == "Natural Language":
                sorted_classifiers["schema:inLanguage"].append(classifier[-1])
            elif classifier[0] == "Programming Language":
                if classifier[1] == "Python" and len(classifier) > 2:
                    if classifier[2] == "Free Threading":
                        temp = "Python Free Threading" \
                               f"{f' {classifier[3]}' if len(classifier) > 3 else ''}"
                    elif classifier[2] == "Implementation":
                        temp = classifier[3] if len(classifier) > 3 else "Python Implementation"
                    else:
                        temp = f"Python {classifier[2]}"
                    sorted_classifiers["schema:programming Language"].append(temp)
                else:
                    sorted_classifiers["schema:programming Language"].append(classifier[-1])
            elif classifier[0] == "Topic":
                temp = {"@type": "schema:Thing", "schema:name": " ".join(classifier[1:])}
                sorted_classifiers["schema:about"].append(temp)

        # add everything to the SoftwareMetadata object
        for key, value in sorted_classifiers.items():
            if len(value) > 1:
                data[key] = value
            elif len(value) == 1:
                data[key] = value[0]

    @classmethod
    def handle_urls(cls, urls: dict[str, str], data):
        """
        Sort all given urls by their label in the dictionary into the schema or codemeta field and
        store them in the given SoftwareMetadata object.

        Parameter
        ---------
        urls: dict[str, str]
            The dictionary mapping a url to its label.
        data: SoftwareMetadata
            The SoftwareMetadata object in which the classifiers are to be stored.

        Returns
        -------
        None

        Raises
        ------
        Nothing
        """

        if not isinstance(urls, dict):
            return

        sorted_urls = {
            "schema:codeRepository": [], "schema:discussionURL": [], "buildInstructions": [],
            "IssueTracker": [], "readme": [], "relatedLink": []
        }
        # iterate over the dictionaries items and add the url to the correct bucket
        # if the key hints it to be the right one
        for name, url in urls.items():
            if (not (isinstance(name, str) and isinstance(url, str))) or url == "":
                continue
            name = name.lower()
            if name.find("code") != -1 or name.find("repository") != -1:
                sorted_urls["schema:codeRepository"].append(url)
            elif name.find("discuss") != -1:
                sorted_urls["schema:discussionURL"].append(url)
            elif name.find("build") != -1 or name.find("instructions") != -1:
                sorted_urls["buildInstructions"].append(url)
            elif name.find("issue") != -1 or name.find("bug") != -1 or name.find("tracker") != -1:
                sorted_urls["IssueTracker"].append(url)
            elif name.find("readme") != -1:
                sorted_urls["readme"].append(url)
            else:
                sorted_urls["relatedLink"].append(url)

        # add everything to the SoftwareMetadata object
        for key, value in sorted_urls.items():
            value = list(set(value))
            if len(value) > 1:
                data[key] = value
            elif len(value) == 1:
                data[key] = value[0]
