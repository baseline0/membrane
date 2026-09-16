"""Binary encodings for converting quantum basis states to continuous solutions.

Supports:
- Single-bit encoding: 1 bit per dimension (coarse, 2^n solutions)
- Multi-bit encoding: k bits per dimension (fine, 2^(k*n) solutions)
- Gray code: Reduce Hamming distance jumps in encoding
"""


class BinaryEncoding:
    """Encode/decode binary strings to continuous variables."""

    @staticmethod
    def bits_to_value(bits: str, bounds: tuple[float, float]) -> float:
        """Convert binary string to value in bounds.

        Simple mapping: interpret bits as fraction in [0, 1], then scale to bounds.

        Args:
            bits: Binary string (e.g., "1011")
            bounds: (lower, upper) bounds

        Returns:
            Continuous value in bounds
        """
        if not bits:
            return bounds[0]

        # Convert binary string to integer, then normalize to [0, 1]
        as_int = int(bits, 2)
        max_int = 2 ** len(bits) - 1
        fraction = as_int / max_int if max_int > 0 else 0.0

        # Scale to bounds
        lower, upper = bounds
        return lower + fraction * (upper - lower)

    @staticmethod
    def value_to_bits(value: float, bounds: tuple[float, float], n_bits: int) -> str:
        """Convert continuous value to binary string.

        Args:
            value: Continuous value
            bounds: (lower, upper) bounds
            n_bits: Number of bits to use

        Returns:
            Binary string of length n_bits
        """
        lower, upper = bounds
        # Normalize value to [0, 1]
        fraction = (value - lower) / (upper - lower) if upper > lower else 0.0
        fraction = max(0.0, min(1.0, fraction))  # Clip to [0, 1]

        # Convert to integer
        max_int = 2**n_bits - 1
        as_int = int(round(fraction * max_int))

        # Convert to binary string (zero-padded)
        return format(as_int, f"0{n_bits}b")

    @staticmethod
    def gray_to_binary(gray: str) -> str:
        """Convert Gray code to binary.

        Gray code minimizes Hamming distance between consecutive encodings.

        Args:
            gray: Gray code string

        Returns:
            Binary string
        """
        binary = gray[0]  # MSB stays the same
        for i in range(1, len(gray)):
            # XOR with previous binary bit
            bit = str(int(binary[i - 1]) ^ int(gray[i]))
            binary += bit
        return binary

    @staticmethod
    def binary_to_gray(binary: str) -> str:
        """Convert binary to Gray code.

        Args:
            binary: Binary string

        Returns:
            Gray code string
        """
        gray = binary[0]  # MSB stays the same
        for i in range(1, len(binary)):
            # XOR consecutive binary bits
            bit = str(int(binary[i - 1]) ^ int(binary[i]))
            gray += bit
        return gray


class MultibitEncoder:
    """Encode/decode basis states using multi-bit representation.

    Maps n-dimensional continuous space to binary basis states where each
    dimension uses k bits for resolution.

    Example: 10D problem with 4 bits per dimension -> 40-bit basis states
    """

    def __init__(self, n_dims: int, n_bits_per_dim: int, bounds: tuple[float, float]):
        """Initialize encoder.

        Args:
            n_dims: Problem dimensionality
            n_bits_per_dim: Bits to use per dimension
            bounds: (lower, upper) bounds for all dimensions
        """
        self.n_dims = n_dims
        self.n_bits_per_dim = n_bits_per_dim
        self.bounds = bounds
        self.total_bits = n_dims * n_bits_per_dim

    def basis_state_to_solution(self, basis_state: str) -> list[float]:
        """Decode basis state to solution vector.

        Args:
            basis_state: Binary string of length total_bits

        Returns:
            List of n_dims continuous values
        """
        if len(basis_state) != self.total_bits:
            # Pad or truncate if needed
            if len(basis_state) < self.total_bits:
                basis_state = basis_state.ljust(self.total_bits, "0")
            else:
                basis_state = basis_state[: self.total_bits]

        solution = []
        for dim in range(self.n_dims):
            # Extract bits for this dimension
            start = dim * self.n_bits_per_dim
            end = start + self.n_bits_per_dim
            dim_bits = basis_state[start:end]

            # Decode to value
            value = BinaryEncoding.bits_to_value(dim_bits, self.bounds)
            solution.append(value)

        return solution

    def solution_to_basis_state(self, solution: list[float]) -> str:
        """Encode solution vector to basis state.

        Args:
            solution: List of n_dims continuous values

        Returns:
            Binary string of length total_bits
        """
        if len(solution) != self.n_dims:
            raise ValueError(f"Solution has {len(solution)} dims, expected {self.n_dims}")

        bits = ""
        for dim in range(self.n_dims):
            dim_bits = BinaryEncoding.value_to_bits(solution[dim], self.bounds, self.n_bits_per_dim)
            bits += dim_bits

        return bits

    def get_basis_dimension(self) -> int:
        """Get the size of basis state space (2^total_bits)."""
        return 2**self.total_bits

    def random_basis_state(self) -> str:
        """Generate random basis state.

        Returns:
            Random binary string of length total_bits
        """
        import random

        return "".join(random.choice("01") for _ in range(self.total_bits))


class ProgressiveEncoding:
    """Encoding that increases resolution over generations.

    Start with coarse encoding (1-2 bits per dim), gradually increase
    to finer encoding (4-8 bits per dim) for refined search.
    """

    def __init__(
        self,
        n_dims: int,
        min_bits_per_dim: int = 1,
        max_bits_per_dim: int = 8,
        bounds: tuple[float, float] = (-5.0, 5.0),
    ):
        """Initialize progressive encoder.

        Args:
            n_dims: Problem dimensionality
            min_bits_per_dim: Starting resolution
            max_bits_per_dim: Target resolution
            bounds: Variable bounds
        """
        self.n_dims = n_dims
        self.min_bits = min_bits_per_dim
        self.max_bits = max_bits_per_dim
        self.bounds = bounds
        self.current_bits = min_bits_per_dim

    def set_generation(self, current_gen: int, total_gens: int) -> None:
        """Update encoding resolution based on generation progress.

        Args:
            current_gen: Current generation number
            total_gens: Total generations in run
        """
        if total_gens == 0:
            self.current_bits = self.min_bits
            return

        # Linear progression from min to max
        progress = current_gen / total_gens
        self.current_bits = int(self.min_bits + (self.max_bits - self.min_bits) * progress)
        self.current_bits = max(self.min_bits, min(self.max_bits, self.current_bits))

    def get_encoder(self) -> MultibitEncoder:
        """Get encoder with current resolution.

        Returns:
            MultibitEncoder using current_bits per dimension
        """
        return MultibitEncoder(self.n_dims, self.current_bits, self.bounds)
