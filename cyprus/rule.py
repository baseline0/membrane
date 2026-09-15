class Rule(object):
    def __init__(self, name: str, req, out, pri: int = 1) -> None:

        self.name = name
        self.requirements = req
        self.output = out
        self.priority = pri

    def __str__(self):
        if self.name != None:
            return f"{self.requirements} -> {self.output} ({self.priority})[{self.name}])"
        else:
            return f"{self.requirements} -> {self.output} ({self.priority})"

    def __repr__(self):
        return self.__str__()
