import collections


def shortestPath(matrix, snake_head_x, snake_head_y, treat_x, treat_y):
    R, C = len(matrix), len(matrix[0])
    shortest_path = collections.deque()
    matrix[snake_head_x][snake_head_y] = 2
    q = collections.deque()
    q.append((snake_head_x, snake_head_y, 0))
    all_check = collections.deque()
    all_check.append((snake_head_x, snake_head_y))
    parent = collections.deque()
    parent.append((snake_head_x, snake_head_y))
    goal = (treat_x, treat_y)
    parent_coord = []

# make a list of all possible cells by BFS before meeting the condition
    while q:
        row, column, layer = q.popleft()
        if row == treat_x and column == treat_y:
            break

# try all possibilities
        for new_row, new_column in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
            if 0 <= new_row < R and 0 <= new_column < C and matrix[new_row][new_column] == 0:
                matrix[new_row][new_column] = 2
                q.append((new_row, new_column, layer + 1))
                all_check.append((new_row, new_column))
                parent.append((row, column))

# find shortest path by tracking back all coordinates that fit conditions
    while goal != all_check[0]:
        for i in all_check:
            if i == goal:
                # print(i)
                shortest_path.append(i)
                # get index by value
                child_index = all_check.index(i)
                parent_coord = parent[child_index]
                goal = parent_coord
        if goal not in all_check:
            shortest_path = all_check
            return shortest_path

    if len(shortest_path) == 1:
        shortest_path.appendleft((0, 0))

    shortest_path.append(parent_coord)
    shortest_path.reverse()
    return shortest_path
