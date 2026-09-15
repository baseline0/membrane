from cyprus.particle import Particle


class DissolveParticle(Particle):
    def __init__(self, target=None):
        self.target = target

    def __str__(self):
        if self.target:
            return f"${self.target}"
        else:
            return "$"

    def __eq__(self, other):
        if isinstance(other, DissolveParticle):
            return other.target == self.target
        else:
            return False
