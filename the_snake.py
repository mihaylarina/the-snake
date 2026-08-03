import random

import pygame as pg

# Инициализация PyGame:
pg.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Параметры текста
SCORE_FONT = pg.font.SysFont('arial', 24)
TEXT_COLOR = (255, 255, 255)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Стартовая позиция змейки
SNAKE_START_POSITION = [(0, 40)]

# Скорость движения змейки:
SPEED = 5

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


def handle_keys(game_object):
    """Отвечает за корректный выход из игры
    и изменение направления движения змейки.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def check_apple_collision(snake, apple):
    """Проверяет, съела ли змея яблоко.
    Если съела, то увеличивает длину и перерисовывает положение яблока.
    """
    if snake.get_head_position() == apple.position:
        snake.length += 1
        apple.randomize_position(snake.get_head_position())


def draw_grid(surface):
    """Рисует сетку на игровом поле с заданным размером ячеек."""
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pg.draw.line(surface, BORDER_COLOR, (x, 0), (x, SCREEN_HEIGHT))

    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pg.draw.line(surface, BORDER_COLOR, (0, y), (SCREEN_WIDTH, y))


def draw_score(surface, length):
    """Рисует текущий счет в верхнем левом углу экрана."""
    score_surface = SCORE_FONT.render(
        f'Score: {length - 1}',
        True,
        TEXT_COLOR,
        BOARD_BACKGROUND_COLOR)
    surface.blit(score_surface, (10, 10))


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для всех объектов поля.
    Attributes:
        body_color (tuple[int, int, int]): Цвет объекта в формате RGB.
        position (tuple[int, int]): Координаты объекта (x, y) на игровой сетке.
    """

    def __init__(self, body_color=None):
        self.body_color = body_color
        self.position = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def draw(self):
        """Абстрактный метод для отрисовки объекта на экране."""
        raise NotImplementedError(
            f'Метод draw() не реализован в классе {type(self).__name__}'
        )

    def draw_one_square(self, position):
        """Метод отрисовывает квадрат заданного размера и цвета"""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс, представляющий яблоко и управляющий его месторасположением.
    Наследуется от GameObject.
    Attributes:
        body_color (tuple[int, int, int]): Цвет объекта в формате RGB.
        position (tuple[int, int]): Координаты объекта (x, y) на игровой сетке.
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position()

    def randomize_position(self, occupied_position=[]):
        """Случайным образом выбирает координаты яблока."""
        while True:
            self.position = (random.randrange(0, SCREEN_WIDTH, GRID_SIZE),
                             random.randrange(0, SCREEN_HEIGHT, GRID_SIZE))
            if self.position not in occupied_position:
                break

    def draw(self):
        """Метод отрисовывает яблоко на экране."""
        self.draw_one_square(self.position)


class Snake(GameObject):
    """
    Класс, представляющий змейку и управляющий её движением.

    Наследуется от GameObject. Отвечает за рост змейки,
    обработку поворотов, проверку столкновений с хвостом и отрисовку.

    Attributes:
        length (int): Текущая длина змейки.
        positions (list[tuple[int, int]]):
            Список координат всех сегментов змейки.
            Первый элемент (positions[0]) — голова.
        direction (tuple[int, int]):
            Текущее направление движения (UP, DOWN, LEFT, RIGHT).
        next_direction (tuple[int, int] | None):
            Новое направление, заданное игроком,
            которое применится на следующем шаге.
        last (tuple[int, int] | None): Координаты последнего удаленного
        сегмента хвоста, необходимые для его затирания на экране.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Метод отвечает за движение змейки."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        next_head_position = (
            (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, next_head_position)
        self.last = self.positions.pop() if len(self.positions) > self.length \
            else None

    def reset(self):
        """Устанавливает стартовые значения атрибутам:
        self.length, self.positions, self.direction, self.next_direction
        и self.last
        """
        self.length = 1
        self.positions = SNAKE_START_POSITION
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def draw(self):
        """Метод отрисовывает змейку на поле."""
        self.draw_one_square(self.positions[0])
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def update_direction(self):
        """Метод, обновляющий направление движения."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def main():
    """Игровой цикл."""
    snake = Snake(SNAKE_COLOR)
    apple = Apple(APPLE_COLOR)
    while True:
        clock.tick(SPEED)
        draw_grid(screen)

        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()
        check_apple_collision(snake, apple)

        apple.draw()
        snake.draw()

        draw_score(screen, snake.length)

        pg.display.update()


if __name__ == '__main__':
    main()
