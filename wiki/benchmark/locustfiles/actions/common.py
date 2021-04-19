import pathlib

def inReferencePath(path):
    return "{}/{}".format(str(pathlib.Path(__file__).parent.parent.parent.absolute()), path)

def writeFile(path, content):
    with open(inReferencePath(path), "w") as f:
        f.write(content)

def readFile(path):
    with open(inReferencePath(path)) as f:
        return f.read()