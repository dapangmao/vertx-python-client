import sys


class Bumper:
    def __init__(self, increment: str):
        self.version = None
        self.increment = increment

    def bump_setup(self):
        res = []
        with open("setup.py", 'r') as infile:
            for l in infile:
                if 'version' in l:
                    start = l.index("'")
                    end = l.index(",")
                    version = l[start + 1: end - 1]
                    print(f"Current version is {version}")
                    _version = [0, 0, 0]
                    for i, x in enumerate(version.split('.')):
                        _version[i] = int(x)
                    if self.increment == 'major':
                        _version[0] += 1
                        _version[1] = 0
                        _version[2] = 0
                    elif self.increment == 'minor':
                        _version[1] += 1
                        _version[2] = 0
                    else:
                        _version[2] += 1
                    self.version = '.'.join(str(x) for x in _version)
                    print(f"Next version is {self.version}")
                    res.append(f"    version='{self.version}',\n")
                else:
                    res.append(l)

        with open("setup.py", 'w') as outfile:
            for l in res:
                outfile.writelines(l)
        return self

    def bump_readme(self):
        res = []
        with open("README.md", 'r') as infile:
            for l in infile:
                if 'pip install' in l:
                    start = l.index("@v")
                    res.append(l[:start] + f"@v{self.version}\n")
                else:
                    res.append(l)
        with open("README.md", 'w') as outfile:
            for l in res:
                outfile.writelines(l)
        return self

    def bump_git_tag(self):
        commands = f"git tag -a v{self.version}".split() + ['-m'] + [f'"Bump version to {self.version}"']
        print("------------ use the commands below to add tag after git commit ------------")
        print(' '.join(commands))
        return self

    def bump_build_sh(self):
        res = []
        with open('build.sh', 'r') as infile:
            for i, l in enumerate(infile):
                if i == 0:
                    res.append(f"export VERSION={self.version}\n")
                else:
                    res.append(l)
        with open("build.sh", 'w') as outfile:
            for l in res:
                outfile.writelines(l)
        return self


if __name__ == '__main__':
    arg = sys.argv[1].strip() if len(sys.argv) > 1 else ''
    Bumper(arg).bump_setup().bump_readme().bump_build_sh().bump_git_tag()
