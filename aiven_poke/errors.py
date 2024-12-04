class PokeError(Exception):
    pass


class KubernetesError(PokeError):
    pass


class NoTopicsFoundError(PokeError):
    """Raised when no topics are found in the cluster

    This is typically a sign that aiven-poke is misconfigured or running in the wrong cluster.
    """
