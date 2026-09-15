from cyprus.particle import Particle


class OsmoseParticle(Particle):
    def __init__(self, payload: str, target=None):

        self.payload = payload
        self.target = target

    def __str__(self):

        if self.target:
            return f"!{self.payload}!!{self.target}"
        else:
            return f"!{self.payload}"

    def __eq__(self, other):

        if isinstance(other, OsmoseParticle):
            return (self.target, self.payload) == (other.target, other.payload)
        else:
            return False
