class Distance:
    def __init__(self, left: int, front: int, right: int) -> None:
        self.left = left
        self.front = front
        self.right = right

    def __str__(self) -> str:
        return f"Distance(left: {self.left}, front: {self.front}, right: {self.right})"
