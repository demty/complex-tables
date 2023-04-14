from typing import Any


class ColCells:
    def generate_empty_arr(self, x_len, y_len):
        res = []
        for i in range(x_len):
            res.append([])
            for j in range(y_len):
                res[i].append(None)
        return res

    def draw(self):
        results = []
        for cell in self.cells:
            items: list[list[Any]] = cell.draw()
            results.append(items)
        max_len = max([len(x) for x in results])
        # add missing rows to the bottom for each result in results
        for r in results:
            max_width_per_elem = max([len(x) for x in r])
            to_add = max_len - len(r)
            r.extend(self.generate_empty_arr(to_add, max_width_per_elem))


def generate_table(data, schema):
    return None
