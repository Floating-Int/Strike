from node import Node


class Splicer:
    NONE = "."
    EMPTY = "."

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def concatenate(self, node_array: list, camera: Node) -> list:
        array = [[self.NONE] * self.width for _y in range(self.height)]
        for node in node_array:
            if not node.visible:
                continue
            content = node._render() # returns 2D array
            if not content:
                continue

            if int(node.x - camera.x) > self.width:
                continue
            static_y = int(node.y - camera.y)
            if static_y >= self.height:
                continue

            for h, line in enumerate(content):
                length = len(line)
                x = int(node.x - camera.x)
                y = static_y + h
                if y > self.height or y < 0:
                    continue
                if x + length < 1:
                    continue
                x_start = 0 if x >= 0 else -x
                x = max(0, x)
                x_end = x + length
                original = array[y][x:x_end]
                spliced = [a if a != self.EMPTY else b for a, b in zip(line[x_start:], original)]
                array[y][x:x_end] = spliced
        return array


    def concatenate(self, node_array: list, camera: Node) -> list:
        array = [[self.NONE] * self.width for _y in range(self.height)]
        for node in node_array:
            if not node.visible or not node.content:
                continue
            x = int(node.x - camera.x) # local x
            y = int(node.y - camera.y) # local x
            height = len(node.content)
            width = len(max(node.content, key=len))
            if not width:
                continue
            if x < 0 or x + width > self.width:
                continue
            if y < 0 or y + height > self.height:
                continue
            for h, cells in enumerate(node.content):
                # if node.__class__.__name__ == "Player":
                #     print(width)
                #     print(array[y+h][x:x+width], cells)
                #     exit()
                original = array[y+h][x:x+width]
                spliced = [a if a != self.EMPTY else b for a, b in zip(cells, original)]
                array[y+h][x:x+width] = spliced
        return array