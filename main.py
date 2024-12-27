import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk


class DrawingApp:
    """
    Приложение для рисования на основе Tkinter и Pillow.

    Это приложение позволяет пользователям рисовать на холсте, выбирать цвета,
    выбирать размеры кисти из выпадающего меню и сохранять свои рисунки
    в формате PNG. Холст инициализируется с белым фоном, и пользователи могут
    очищать его или динамически изменять размер кисти.

    Атрибуты:
        root (tk.Tk): Главное окно приложения.
        image (PIL.Image): Объект изображения, который содержит рисунок.
        draw (PIL.ImageDraw): Контекст рисования для изображения.
        canvas (tk.Canvas): Виджет холста для рисования пользователем.
        last_x (int): Последняя координата x события мыши.
        last_y (int): Последняя координата y события мыши.
        pen_color (str): Текущий цвет пера.
        brush_size (int): Текущий размер кисти.

    Методы:
        setup_ui(): Инициализирует компоненты пользовательского интерфейса.
        paint(event): Обрабатывает рисование на холсте.
        reset(event): Сбрасывает координаты last_x и last_y.
        clear_canvas(): Очищает холст и сбрасывает изображение.
        choose_color(): Открывает диалог выбора цвета для выбора цвета пера.
        save_image(): Сохраняет текущее изображение как PNG файл.
        update_brush_size(size): Обновляет размер кисти на основе выбора пользователя.
        activate_eraser(self):   Активация инструмента "Ластик"
        deactivate_eraser(self):   Деактивация инструмента "Ластик" и восстановление предыдущего цвета
    """

    def __init__(self, root):
        '''
         Инициализирует приложение DrawingApp с данным окном root.
        :param root: Главное окно приложения.
        '''
        self.root = root
        self.root.title("Рисовалка с сохранением в PNG")  # Устанавливается заголовок окна приложения.

        self.image = Image.new("RGB", (600, 400),
                               "white")  # Создается объект изображения (self.image) с использованием библиотеки Pillow.
        # Это изображение служит виртуальным холстом, на котором происходит рисование. Изначально оно заполнено белым цветом.

        self.draw = ImageDraw.Draw(
            self.image)  # Инициализируется объект ImageDraw.Draw(self.image), который позволяет рисовать на объекте изображения.

        self.canvas = tk.Canvas(root, width=600, height=600, bg='white', cursor="dot")
        self.canvas.pack()

        self.last_x, self.last_y = None, None
        self.pen_color = "black"
        self.brush_size = 5
        self.eraser_size = 20  # Размер для ластика
        self.is_eraser_active = False  # Флаг для режима ластика
        self.default_cursor = "dot"  # Курсор по умолчанию

        self.setup_ui()
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)

    def setup_ui(self):
        '''
        Этот метод отвечает за создание и расположение виджетов управления:
        '''
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X)

        clear_button = tk.Button(control_frame, text="Очистить", command=self.clear_canvas)
        clear_button.pack(side=tk.LEFT)

        color_button = tk.Button(control_frame, text="Выбрать цвет", command=self.choose_color)
        color_button.pack(side=tk.LEFT)

        save_button = tk.Button(control_frame, text="Сохранить", command=self.save_image)
        save_button.pack(side=tk.LEFT)
        sizes = [1, 2, 5, 10, 20]  # Доступные размеры кисти
        self.brush_size_var = tk.IntVar(value=sizes[2])  # Установка начального значения
        brush_size_menu = tk.OptionMenu(control_frame, self.brush_size_var, *sizes, command=self.update_brush_size)
        brush_size_menu.pack(side=tk.LEFT)
        eraser_button = tk.Button(control_frame, text="Ластик", command=self.activate_eraser)
        eraser_button.pack(side=tk.LEFT)

        eraser_sizes = [5, 10, 20, 30]  # Доступные размеры ластика
        self.eraser_size_var = tk.IntVar(value=self.eraser_size)  # Установка начального значения
        eraser_size_menu = tk.OptionMenu(control_frame, self.eraser_size_var, *eraser_sizes,
                                         command=self.update_eraser_size)
        eraser_size_menu.pack(side=tk.LEFT)

        restore_color_button = tk.Button(control_frame, text="Вернуться обратно в курсор",
                                         command=self.deactivate_eraser)
        restore_color_button.pack(side=tk.LEFT)

    def update_brush_size(self, selected_size):
        '''
         # Обновление размера кисти
        :param selected_size:  Выбранный размер кисти из выпадающего меню.
        '''
        if not self.is_eraser_active:  # Менять размер кисти, только если не активен ластик
            self.brush_size = int(selected_size)
    def update_eraser_size(self, selected_size):
        '''
        Обновляем размер ластика, когда изменен выбор
        :param selected_size: Выбранный размер ластика из выпадающего меню.
        '''
        self.eraser_size = int(selected_size)  # Обновляем размер ластика, когда изменен выбор

    def paint(self, event):
        '''
        Функция вызывается при движении мыши с нажатой левой кнопкой по холсту. Она рисует линии на холсте Tkinter и параллельно на объекте Image из Pillow:
        :param event: Событие содержит координаты мыши, которые используются для рисования.
        '''
        # Обработка рисования
        if self.last_x and self.last_y:
            if self.is_eraser_active:
                # Координаты квадрата для ластика
                x1 = event.x - self.eraser_size // 2
                y1 = event.y - self.eraser_size // 2
                x2 = event.x + self.eraser_size // 2
                y2 = event.y + self.eraser_size // 2

                # Рисуем "ластик" (белый квадрат)
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="white")
                self.draw.rectangle([x1, y1, x2, y2], fill="white")  # Также стираем в изображении
            else:
                # Рисуем линию
                self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                        width=self.brush_size, fill=self.pen_color,
                                        capstyle=tk.ROUND, smooth=tk.TRUE)
                self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.pen_color,
                               width=self.brush_size)
        self.last_x = event.x
        self.last_y = event.y

    def reset(self, event):
        '''
        Сбрасывает последние координаты кисти. Это необходимо для корректного начала новой линии после того, как пользователь отпустил кнопку мыши и снова начал рисовать.
        :param event: Событие мыши при отпускании кнопки.
        '''
        self.last_x, self.last_y = None, None

    def clear_canvas(self):
        '''
         Очищает холст, удаляя все нарисованное, и пересоздает объекты Image и ImageDrawдля нового изображения.
        '''
        self.canvas.delete("all")
        self.image = Image.new("RGB", (600, 400), "white")
        self.draw = ImageDraw.Draw(self.image)

    def choose_color(self):
        '''
        Открывает стандартное диалоговое окно выбора цвета и устанавливает выбранный цвет как текущий для кисти.
        '''
        # Выбор цвета
        color = colorchooser.askcolor()[1]
        if color:
            self.previous_color = self.pen_color  # Сохраняем предыдущий цвет
            self.pen_color = color

    def save_image(self):
        '''
        Позволяет пользователю сохранить изображение, используя стандартное диалоговое окно для сохранения файла.
        Поддерживает только формат PNG. В случае успешного сохранения выводится сообщение об успешном сохранении.
        '''
        file_path = filedialog.asksaveasfilename(filetypes=[('PNG files', '*.png')])
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
            self.image.save(file_path)
            messagebox.showinfo("Информация", "Изображение успешно сохранено!")

    def activate_eraser(self):
        '''
        Активация инструмента "Ластик"
        '''
        self.is_eraser_active = True
        self.canvas.config(cursor="circle")  # Изменяем курсор на круг

    def deactivate_eraser(self):
        '''
        Деактивация инструмента "Ластик" и восстановление предыдущего цвета
        '''
        self.is_eraser_active = False
        self.canvas.config(cursor="dot")  # Сбрасываем курсор на стрелку

def main():
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
