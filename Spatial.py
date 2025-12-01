# Spatial.py
import math

class SpatialGrid:
    def __init__(self, cell_size=100):
        self.cell_size = cell_size
        self.cells = {}

    def _cell_coords(self, x, z):
        """Chuyển toạ độ thế giới -> toạ độ ô lưới"""
        return (int(x // self.cell_size), int(z // self.cell_size))

    def clear(self):
        self.cells.clear()

    def insert(self, obj, x, z):
        """Thêm đối tượng vào đúng ô"""
        cell = self._cell_coords(x, z)
        if cell not in self.cells:
            self.cells[cell] = []
        self.cells[cell].append(obj)

    def nearby(self, x, z, radius):
        """Trả về tất cả đối tượng trong phạm vi radius"""
        cx, cz = self._cell_coords(x, z)
        r = math.ceil(radius / self.cell_size)
        result = []
        for i in range(cx - r, cx + r + 1):
            for j in range(cz - r, cz + r + 1):
                if (i, j) in self.cells:
                    result.extend(self.cells[(i, j)])
        return result
