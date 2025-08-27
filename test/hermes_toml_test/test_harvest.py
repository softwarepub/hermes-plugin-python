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
    ({}, {}),
    (None, {}),
    ("", {}),
    (1, {}),
    ([], {}),
    ({1: ""}, {}),
    ({None: ""}, {}),
    ({1: "", None: ""}, {}),
    ({"a": []}, {}),
    ({"a": None}, {}),
    ({"a": 1}, {}),
    ({"a": {}}, {}),
    ({"a": 1, "b": None}, {}),
    ({"a": ""}, {}),
    ({"a": "b"}, {"relatedLink": "b"}),
    ({"a": "b", "b": None}, {"relatedLink": "b"}),
    ({"code": "a"}, {"schema:codeRepository": "a"}),
    ({"a": "b", "b": "c"}, {"relatedLink": unordered(["b", "c"])}),
    ({"codeRepository": "a"}, {"schema:codeRepository": "a"}),
    ({"repository": "a"}, {"schema:codeRepository": "a"}),
    ({"code": "a", "repository": "b"}, {"schema:codeRepository": unordered(["a", "b"])}),
    ({"code": "a", "repository": "a"}, {"schema:codeRepository": "a"}),
    ({"buildInstructions": "a"}, {"buildInstructions": "a"}),
    ({"IssueTracker": "a"}, {"IssueTracker": "a"}),
    ({"readme": "a"}, {"readme": "a"}),
    ({"discussion": "a"}, {"schema:discussionURL": "a"}),
    ({"readme": "a", "code": "b", "homepage": "c"},
     {"readme": "a", "schema:codeRepository": "b", "relatedLink": "c"}),
    ({"readme": "a", "code": "b", "homepage": "c", "mymistake": "c"},
     {"readme": "a", "schema:codeRepository": "b", "relatedLink": "c"}),
    ({"readme": "a", "code": "b", "homepage": "c", "mypage": "d"},
     {"readme": "a", "schema:codeRepository": "b", "relatedLink": unordered(["c", "d"])})
])
def test_handle_urls(in_data, out_data):
    TomlHarvestPlugin.handle_urls(in_data, data := {})
    assert data == out_data

@pytest.mark.parametrize("in_data, out_data", [
    (1, {}),
    ({}, {}),
    ("", {}),
    ([], {}),
    ([""], {}),
    (["", ""], {}),
    ([1], {}),
    ("Development Status :: xxx", {}),
    ("Environment :: xxx", {}),
    ("Framework :: xxx", {}),
    ("Intended Audience :: xxx",
     {"schema:audience": {"@type": "schema:Audience", "schema:name": "xxx"}}),
    ("License :: xxx", {"schema:license": {"@type": "schema:CreativeWork", "schema:name": "xxx"}}),
    ("License :: OSI Approved", {}),
    ("Operating System :: Microsoft", {}),
    ("License :: OSI Approved :: xxx",
     {"schema:license": {"@type": "schema:CreativeWork", "schema:name": "xxx"}}),
    ("Natural Language :: xxx", {"schema:inLanguage": "xxx"}),
    ("Operating System :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: x :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: x :: x :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: Microsoft :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Programming Language :: xxx", {"schema:programming Language": "xxx"}),
    (["Programming Language :: xxx", 1], {"schema:programming Language": "xxx"}),
    ("Programming Language :: Python :: xxx", {"schema:programming Language": "Python xxx"}),
    ("Programming Language :: Python :: x :: only", {"schema:programming Language": "Python x"}),
    ("Programming Language :: Python :: Free Threading :: xxx",
     {"schema:programming Language": "Python Free Threading xxx"}),
    ("Programming Language :: Python :: Implementation :: x", {"schema:programming Language": "x"}),
    ("Topic :: a", {"schema:about": {"@type": "schema:Thing", "schema:name": "a"}}),
    ("Topic :: a :: b", {"schema:about": {"@type": "schema:Thing", "schema:name": "a b"}}),
    ("Topic :: a :: b :: c", {"schema:about": {"@type": "schema:Thing", "schema:name": "a b c"}}),
    ("Topic :: a :: b :: c :: d",
     {"schema:about": {"@type": "schema:Thing", "schema:name": "a b c d"}}),
    (["Natural Language :: xxx", "Natural Language :: xxx"], {"schema:inLanguage": "xxx"}),
    (["Natural Language :: xxx", "Natural Language :: yyy"],
     {"schema:inLanguage": unordered(["xxx", "yyy"])}),
    (["Natural Language :: xxx", "Programming Language :: xxx"],
     {"schema:inLanguage": "xxx", "schema:programming Language": "xxx"}),
    (["Natural Language :: xxx", "Programming Language :: xxx", "Programming Language :: xxx"],
     {"schema:inLanguage": "xxx", "schema:programming Language": "xxx"}),
    (["Natural Language :: xxx", "Programming Language :: xxx", "Programming Language :: yyy"],
     {"schema:inLanguage": "xxx", "schema:programming Language": unordered(["xxx", "yyy"])}),
    (["Topic :: a", "Topic :: b"],
     {"schema:about": unordered([{"@type": "schema:Thing", "schema:name": "a"},
                                 {"@type": "schema:Thing", "schema:name": "b"}])})
])
def test_handle_pypi_classifiers(in_data, out_data):
    TomlHarvestPlugin.handle_pypi_classifieres(in_data, data := {})
    assert data == out_data

@pytest.mark.parametrize("in_data, out_data", [
    (1, {}),
    ([], {}),
    ({}, {}),
    ("", {}),
    ("abc <abc@abc.abc>",
     {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}),
    ("abc@abc.abc", {"schema:email": "abc@abc.abc", "@type": "schema:Person"}),
    ("abc.ab.c@abc.abc", {"schema:email": "abc.ab.c@abc.abc", "@type": "schema:Person"}),
    ("abc@abc.ab.c.abc", {"schema:email": "abc@abc.ab.c.abc", "@type": "schema:Person"}),
    ("abc", {"schema:name": "abc", "@type": "schema:Person"}),
    ("a bc", {"schema:name": "a bc", "@type": "schema:Person"}),
    ({"name": "abc", "email": "abc@abc.abc"},
     {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}),
    ({"email": "abc@abc.abc"}, {"schema:email": "abc@abc.abc", "@type": "schema:Person"}),
    ({"name": "abc"}, {"schema:name": "abc", "@type": "schema:Person"}),
    ({"name": "abc", "email": "abc@abc.abc", "a": "b"},
     {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}),
    ({"email": "abcabc.abc"}, {}),
    ({"email": "abc@abcabc"}, {}),
    ({"email": "@abc.abc"}, {}),
    ({"email": "abc@"}, {}),
    ({"email": "abc@.abc"}, {}),
    ({"email": "abc@."}, {}),
    ({"email": "abc@abc."}, {}),
    ({"email": "abc.@abc.abc"}, {}),
    ({"email": ".@abc.abc"}, {}),
    ({"email": "abc@@abc.abc"}, {}),
    ({"email": "abc#@abc.abc"}, {}),
    ({"email": "a bc@a.a"}, {}),
    ({"name": "abc", "email": "abcabc.abc"}, {"schema:name": "abc", "@type": "schema:Person"}),
    ({"name": "abc", "email": 1}, {"schema:name": "abc", "@type": "schema:Person"}),
    ({"name": "abc", "email": []}, {"schema:name": "abc", "@type": "schema:Person"}),
    ({"name": 1, "email": "abc@abc.abc"},
     {"schema:email": "abc@abc.abc", "@type": "schema:Person"}),
    ({"name": [], "email": "abc@abc.abc"},
     {"schema:email": "abc@abc.abc", "@type": "schema:Person"})
])
def test_extract_personal_data(in_data, out_data):
    assert TomlHarvestPlugin.extract_personal_data(in_data) == out_data

@pytest.mark.parametrize("person_data, key, out_data", [
    (1, "x", {}),
    ([], "x", {}),
    ({}, "x", {}),
    ("", "x", {}),
    ("", 1, {}),
    ("", [], {}),
    ("", {}, {}),
    ("abc <abc@abc.abc>", "x",
     {"x": {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ("abc@abc.abc", "x", {"x": {"schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ("abc.ab.c@abc.abc", "x",
     {"x": {"schema:email": "abc.ab.c@abc.abc", "@type": "schema:Person"}}),
    ("abc@abc.ab.c.abc", "x",
     {"x": {"schema:email": "abc@abc.ab.c.abc", "@type": "schema:Person"}}),
    ("abc", "x", {"x": {"schema:name": "abc", "@type": "schema:Person"}}),
    ("a bc", "x", {"x": {"schema:name": "a bc", "@type": "schema:Person"}}),
    ({"name": "abc", "email": "abc@abc.abc"}, "x",
     {"x": {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ({"email": "abc@abc.abc"}, "x",
     {"x": {"schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ({"name": "abc"}, "x", {"x": {"schema:name": "abc", "@type": "schema:Person"}}),
    ({"name": "abc", "email": "abc@abc.abc", "a": "b"}, "x",
     {"x": {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ({"email": "abcabc.abc"}, "x", {}),
    ({"email": "abc@abcabc"}, "x", {}),
    ({"email": "@abc.abc"}, "x", {}),
    ({"email": "abc@"}, "x", {}),
    ({"email": "abc@.abc"}, "x", {}),
    ({"email": "abc@."}, "x", {}),
    ({"email": "abc@abc."}, "x", {}),
    ({"email": "abc.@abc.abc"}, "x", {}),
    ({"email": ".@abc.abc"}, "x", {}),
    ({"email": "abc@@abc.abc"}, "x", {}),
    ({"email": "abc#@abc.abc"}, "x", {}),
    ({"email": "a bc@a.a"}, "x", {}),
    ({"name": "abc", "email": "abcabc.abc"}, "x",
     {"x": {"schema:name": "abc", "@type": "schema:Person"}}),
    ({"name": "abc", "email": 1}, "x", {"x": {"schema:name": "abc", "@type": "schema:Person"}}),
    ({"name": "abc", "email": []}, "x", {"x": {"schema:name": "abc", "@type": "schema:Person"}}),
    ({"name": 1, "email": "abc@abc.abc"}, "x",
     {"x": {"schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ({"name": [], "email": "abc@abc.abc"}, "x",
     {"x": {"schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ([{"name": "abc", "email": "abc@abc.abc"}], "x",
     {"x": {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}}),
    ([{"name": "ab", "email": "ab@ab.ab"}, {"name": "a", "email": "a@a.a"}], "x",
     {"x": unordered([{"schema:name": "ab", "schema:email": "ab@ab.ab", "@type": "schema:Person"},
                      {"schema:name": "a", "schema:email": "a@a.a", "@type": "schema:Person"}])}),
    ([{"name": "abc", "email": "abc@abc.abc"}, 1], "x",
     {"x": {"schema:name": "abc", "schema:email": "abc@abc.abc", "@type": "schema:Person"}})
])
def test_handle_person(person_data, key, out_data):
    TomlHarvestPlugin.handle_person(person_data, key, data := {})
    assert data == out_data

@pytest.mark.parametrize("in_data, out_data", [
    ({"keywords": 1, "dist-name": [], "module": {}}, {}),
    ({"keywords": ["a", "b"], "dist-name": ["c"], "module": "d"},
     {"schema:keywords": unordered(["a", "b"]), "schema:name": "c", "schema:alternateName": "d"}),
    ({"keywords": ["a", 1], "dist-name": ["b", []], "module": ["c", {}]},
     {"schema:keywords": "a", "schema:name": "b", "schema:alternateName": "c"}),
    ({"keywords": ["a", "b", 1], "dist-name": ["c", "d", []], "module": ["e", "f", {}]},
     {"schema:keywords": unordered(["a", "b"]), "schema:name": unordered(["c", "d"]),
      "schema:alternateName": unordered(["e", "f"])}),
    ({"keywords": [1], "dist-name": [1, []]}, {}),
    ({"keywords": ["a", "a", 1], "dist-name": ["b", "c", "c"], "module": ["d", "d"]},
     {"schema:keywords": "a", "schema:name": unordered(["b", "c"]), "schema:alternateName": "d"}),
    ({"author": "A", "author-email": "a@a.a", "maintainer": "B", "maintainer-email": "b@b.b"},
     {"schema:author": {"schema:name": "A", "schema:email": "a@a.a", "@type": "schema:Person"},
      "schema:maintainer": {"schema:name": "B", "schema:email": "b@b.b",
                            "@type": "schema:Person"}}),
    ({"author": "A", "maintainer-email": "b@b.b"},
     {"schema:author": {"schema:name": "A", "@type": "schema:Person"},
      "schema:maintainer": {"schema:email": "b@b.b", "@type": "schema:Person"}}),
    ({"author-email": "a@a.a", "maintainer": "B"},
     {"schema:author": {"schema:email": "a@a.a", "@type": "schema:Person"},
      "schema:maintainer": {"schema:name": "B", "@type": "schema:Person"}}),
    ({"author": "A", "author-email": "a@a.", "maintainer": "B", "maintainer-email": "@b.b"},
     {"schema:author": {"schema:name": "A", "@type": "schema:Person"},
      "schema:maintainer": {"schema:name": "B", "@type": "schema:Person"}}),
    ({"author": "", "maintainer-email": "b@.b"}, {}),
    ({"author-email": "aa.a", "maintainer": ""}, {}),
    ({"classifiers": ""}, {}),
    ({"classifiers": []}, {}),
    ({"classifiers": ["", 1, [], {}, "Development Status :: xxx", "Environment :: xxx",
                      "Framework :: xxx", "License :: OSI Approved",
                      "Operating System :: Microsoft", "Intended Audience :: xxx",
                      "License :: xxx"]},
     {"schema:audience": {"@type": "schema:Audience", "schema:name": "xxx"},
      "schema:license": {"@type": "schema:CreativeWork", "schema:name": "xxx"}}),
    ("License :: OSI Approved :: xxx",
     {"schema:license": {"@type": "schema:CreativeWork", "schema:name": "xxx"}}),
    ("Natural Language :: xxx", {"schema:inLanguage": "xxx"}),
    ("Operating System :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: x :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: x :: x :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Operating System :: Microsoft :: xxx",
     {"schema:targetProduct": {"@type": "schema:SoftwareApplication", "schema:name": "xxx"}}),
    ("Programming Language :: xxx", {"schema:programming Language": "xxx"}),
    (["Programming Language :: xxx", 1], {"schema:programming Language": "xxx"}),
    ("Programming Language :: Python :: xxx", {"schema:programming Language": "Python xxx"}),
    ("Programming Language :: Python :: x :: only", {"schema:programming Language": "Python x"}),
    ("Programming Language :: Python :: Free Threading :: xxx",
     {"schema:programming Language": "Python Free Threading xxx"}),
    ("Programming Language :: Python :: Implementation :: x", {"schema:programming Language": "x"}),
    ("Topic :: a", {"schema:about": {"@type": "schema:Thing", "schema:name": "a"}}),
    ("Topic :: a :: b", {"schema:about": {"@type": "schema:Thing", "schema:name": "a b"}}),
    ("Topic :: a :: b :: c", {"schema:about": {"@type": "schema:Thing", "schema:name": "a b c"}}),
    ("Topic :: a :: b :: c :: d",
     {"schema:about": {"@type": "schema:Thing", "schema:name": "a b c d"}}),
    (["Natural Language :: xxx", "Natural Language :: xxx"], {"schema:inLanguage": "xxx"}),
    (["Natural Language :: xxx", "Natural Language :: yyy"],
     {"schema:inLanguage": unordered(["xxx", "yyy"])}),
    (["Natural Language :: xxx", "Programming Language :: xxx"],
     {"schema:inLanguage": "xxx", "schema:programming Language": "xxx"}),
    (["Natural Language :: xxx", "Programming Language :: xxx", "Programming Language :: xxx"],
     {"schema:inLanguage": "xxx", "schema:programming Language": "xxx"}),
    (["Natural Language :: xxx", "Programming Language :: xxx", "Programming Language :: yyy"],
     {"schema:inLanguage": "xxx", "schema:programming Language": unordered(["xxx", "yyy"])}),
    (["Topic :: a", "Topic :: b"],
     {"schema:about": unordered([{"@type": "schema:Thing", "schema:name": "a"},
                                 {"@type": "schema:Thing", "schema:name": "b"}])}),
    ({"author": "A", "author-email": "a@a.a", "maintainer": "B", "maintainer-email": "b@b.b",
      "keywords": ["a", "b"], "dist-name": ["c"], "module": "d"},
     {"schema:keywords": unordered(["a", "b"]), "schema:name": "c", "schema:alternateName": "d",
      "schema:author": {"schema:name": "A", "schema:email": "a@a.a", "@type": "schema:Person"},
      "schema:maintainer": {"schema:name": "B", "schema:email": "b@b.b", "@type": "schema:Person"}})
])
def test_handle_flit_table(in_data, out_data):
    TomlHarvestPlugin.handle_flit_table(in_data, data := {})
    assert data == out_data

@pytest.mark.parametrize("in_data, out_data", [
    ({"name": "a", "version": "x.x.x", "description": "abc", "keywords": ["a", "b", "c"],
      "repository": "xxx"},
     {"schema:name": "a", "schema:version": "x.x.x", "schema:description": "abc",
      "schema:keywords": ["a", "b", "c"], "schema:CodeRepository": "xxx"})
])
def test_handle_poetry_table(in_data, out_data):
    TomlHarvestPlugin.handle_poetry_table(in_data, data := {})
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
