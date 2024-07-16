import toml

def main():
    with open("pyproject.toml", 'r+') as f:
        data = toml.load(f)
        project = data.get("project")
        if not project is None:
            version = project.get("version")
            if not version is None:
                a,b,c = map(int, version.split("."))
                if c < 99:
                    c += 1
                elif b < 99:
                    c = 0
                    b += 1
                else:
                    c = 0
                    b = 0
                    a += 1
                data["project"]["version"] = str(a) + "." + str(b) + "." + str(c)
    if not data == {}:
        with open("pyproject.toml", 'w') as f:
            toml.dump(data, f)

main()
