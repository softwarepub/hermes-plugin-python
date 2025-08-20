# SPDX-FileCopyrightText: 2024 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: Apache-2.0

# SPDX-FileContributor: Michael Meinel
# SPDX-FileContributor: Michael Fritzsche

import pytest
import toml
from pytest_unordered import unordered
from hermes_toml.harvest import TomlHarvestPlugin

@pytest.mark.parametrize("in_data, out_data", [
    ({}, {}), (None, {}), ("", {}), (1, {}), ([], {}), ({1:""}, {}), ({None:""}, {}),
    ({1:"", None:""}, {}), ({"a":[]}, {}), ({"a":None}, {}), ({"a":1}, {}), ({"a":{}}, {}),
    ({"a":1, "b":None}, {}), ({"a":""}, {}), ({"a":"b"}, {"relatedLink":"b"}),
    ({"a":"b", "b":None}, {"relatedLink":"b"}), ({"code": "a"}, {"schema:codeRepository": "a"}),
    ({"a":"b", "b":"c"}, {"relatedLink":unordered(["b", "c"])}),
    ({"codeRepository": "a"}, {"schema:codeRepository": "a"}),
    ({"repository": "a"}, {"schema:codeRepository": "a"}),
    ({"code": "a", "repository":"b"}, {"schema:codeRepository": unordered(["a", "b"])}),
    ({"code": "a", "repository":"a"}, {"schema:codeRepository": "a"}),
    ({"buildInstructions": "a"}, {"buildInstructions": "a"}),
    ({"IssueTracker": "a"}, {"IssueTracker": "a"}), ({"readme": "a"}, {"readme": "a"}),
    ({"discussion": "a"}, {"schema:discussionURL": "a"}),
    ({"readme":"a","code":"b","homepage":"c"},
     {"readme":"a","schema:codeRepository":"b","relatedLink":"c"}),
    ({"readme":"a","code":"b","homepage":"c", "mymistake":"c"},
     {"readme":"a","schema:codeRepository":"b","relatedLink":"c"}),
    ({"readme":"a","code":"b","homepage":"c", "mypage":"d"},
     {"readme":"a","schema:codeRepository":"b","relatedLink":unordered(["c", "d"])})
])
def test_handle_urls(in_data, out_data):
    data = {}
    TomlHarvestPlugin.handle_urls(in_data, data)
    assert data == out_data

@pytest.mark.parametrize("in_data, out_data", [
    (1, {}), ({}, {}), ("", {}), ([], {}), ([""], {}), (["", ""], {}), ([1], {}),
    ("Development Status :: xxx", {}), ("Environment :: xxx", {}), ("Framework :: xxx", {}),
    ("Intended Audience :: xxx", {"schema:audience": {"@type": "schema:Audience", "schema:name": "xxx"}}),
    ("License :: xxx", {"schema:license": {"@type": "schema:CreativeWork", "schema:name": "xxx"}}),
    ("License :: OSI Approved", {}), ("Operating System :: Microsoft", {}),
    ("License :: OSI Approved :: xxx", {"schema:license": {"@type": "schema:CreativeWork", "schema:name": "xxx"}}),
    ("Natural Language :: xxx", {"schema:inLanguage": "xxx"}),
    ("Operating System :: xxx", {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: x :: xxx", {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: x :: x :: xxx", {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: Microsoft :: xxx", {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Programming Language :: xxx", {"schema:programming Language": "xxx"}),
    (["Programming Language :: xxx", 1], {"schema:programming Language": "xxx"}),
    ("Programming Language :: Python :: xxx", {"schema:programming Language": "Python xxx"}),
    ("Programming Language :: Python :: x :: only", {"schema:programming Language": "Python x"}),
    ("Programming Language :: Python :: Free Threading :: xxx", {"schema:programming Language": "Python Free Threading xxx"}),
    ("Programming Language :: Python :: Implementation :: x", {"schema:programming Language": "x"}),
    ("Topic :: a", {"schema:about": {"@type": "schema:Thing", "schema:name": "a"}}),
    ("Topic :: a :: b", {"schema:about": {"@type": "schema:Thing", "schema:name": "a b"}}),
    ("Topic :: a :: b :: c", {"schema:about": {"@type": "schema:Thing", "schema:name": "a b c"}}),
    ("Topic :: a :: b :: c :: d", {"schema:about": {"@type": "schema:Thing", "schema:name": "a b c d"}}),
    (["Natural Language :: xxx", "Natural Language :: xxx"], {"schema:inLanguage": "xxx"}),
    (["Natural Language :: xxx", "Natural Language :: yyy"], {"schema:inLanguage": unordered(["xxx", "yyy"])}),
    (["Natural Language :: xxx", "Programming Language :: xxx"], {"schema:inLanguage": "xxx", "schema:programming Language": "xxx"}),
    (["Natural Language :: xxx", "Programming Language :: xxx", "Programming Language :: xxx"],
     {"schema:inLanguage": "xxx", "schema:programming Language": "xxx"}),
    (["Natural Language :: xxx", "Programming Language :: xxx", "Programming Language :: yyy"],
     {"schema:inLanguage": "xxx", "schema:programming Language": unordered(["xxx", "yyy"])}),
    (["Topic :: a", "Topic :: b"], {"schema:about": unordered([{"@type": "schema:Thing", "schema:name": "a"}, {"@type": "schema:Thing", "schema:name": "b"}])}),
])
def test_handle_pypi_classifiers(in_data, out_data):
    data = {}
    TomlHarvestPlugin.handle_pypi_classifieres(in_data, data)
    assert data == out_data

"""
Test-Cases:
korrekte Eingabe:
{"project": {"keywords": ["A", "B", "C"], "classifiers": ["Development Status :: 1 - Planning", "Environment :: Console"], "readme": {"text": "Test", content-type: "text/markdown"},
             "requires-python": ">=3.12", "name": "Test", "authors": [{"name": "Testi", "email": "testi@domain.de"}, {"name": "Test", "email": "test@otherdomain.com"}],
             "maintainers": [{"name": "Tester", "email": "tester@domain.com"}, {"name": "Testers", "email": "testers@otherdomain.de"}], "dependencies": ["scipy>=1.0", "numpy~=1.5"],
             "license": "MIT AND (Apache-2.0 OR BSD-2-Clause)", "urls": ["homepage": "mypage.org", "documentation": "mydocumentation.com"], "version": "1.5.2"
            }
}


"""
