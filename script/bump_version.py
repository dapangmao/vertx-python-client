import subprocess


class Bumper:
    def __init__(self):
        self.version = None

    def bump_setup(self):
        res = []
        with open("setup.py", 'r') as infile:
            for l in infile:
                if 'version' in l:
                    start = l.index("'")
                    end = l.index(",")
                    version = float(l[start + 1: end - 1])
                    print(f"Current version is {version}")
                    self.version = round(version + 0.10, 1)
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
        print(' '.join(commands))
        subprocess.call(commands)
        return self


if __name__ == '__main__':
    Bumper().bump_setup().bump_readme().bump_git_tag()
