import tkinter as tk
from tkinter import messagebox
import pyperclip

CELL_SIZE = 40
GRID_SIZE = 8

class PixelEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("8x8 Pixel Editor")

        self.canvas = tk.Canvas(root, width=CELL_SIZE * GRID_SIZE, height=CELL_SIZE * GRID_SIZE, bg='white')
        self.canvas.grid(row=0, column=0, columnspan=4)

        self.cells = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.btn_rotate = tk.Button(root, text="Повернуть 90°", command=self.rotate_right)  
        self.btn_rotate.grid(row=3, column=0, columnspan=4, pady=10)
        self.text_output = tk.Text(root, height=10, width=40)
        self.text_output.grid(row=1, column=0, columnspan=4, pady=10)

        self.btn_export = tk.Button(root, text="Скопировать в буфер", command=self.copy_to_clipboard)
        self.btn_export.grid(row=2, column=0)

        self.btn_import = tk.Button(root, text="Вставить из буфера", command=self.paste_from_clipboard)
        self.btn_import.grid(row=2, column=1)

        self.btn_clear = tk.Button(root, text="Очистить", command=self.clear_grid)
        self.btn_clear.grid(row=2, column=2)

        self.btn_render = tk.Button(root, text="Обновить из текстового поля", command=self.load_from_text)
        self.btn_render.grid(row=2, column=3)

        self.draw_grid()
        self.update_text_output()

    def draw_grid(self):
        self.canvas.delete("cell")
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                x0 = x * CELL_SIZE
                y0 = y * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                fill = "black" if self.cells[y][x] else "white"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="gray", tags="cell")

    def toggle_cell(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            self.cells[y][x] ^= 1
            self.draw_grid()
            self.update_text_output()
    def rotate_right(self):
        new_cells = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                new_cells[x][GRID_SIZE - 1 - y] = self.cells[y][x]
        self.cells = new_cells
        self.draw_grid()
        self.update_text_output()

    # def get_byte_array(self):
    #     result = []
    #     for x in range(GRID_SIZE):
    #         byte = 0
    #         for y in range(GRID_SIZE):
    #             byte |= (self.cells[y][x] << (7 - y))
    #         result.append(byte)
    #     return result
    def get_byte_array(self):
        result = []
        for x in range(GRID_SIZE):
            byte = 0
            for y in range(GRID_SIZE):
                byte |= (self.cells[y][x] << y)  # ← главное изменение
            result.append(byte)
        return result
    def update_text_output(self):
        byte_array = self.get_byte_array()
        lines = []
        for i, byte in enumerate(byte_array):
            bin_str = format(byte, '08b')
            vis = ''.join('█' if b == '1' else ' ' for b in bin_str)
            lines.append(f"Столбец {i}: {bin_str}  -> {vis}")
        array_line = "{ " + ', '.join(f"0x{b:02X}" for b in byte_array) + " }"

        self.text_output.delete("1.0", tk.END)
        self.text_output.insert(tk.END, '\n'.join(lines) + '\n\n' + array_line)

    def copy_to_clipboard(self):
        byte_array = self.get_byte_array()
        array_str = "{ " + ', '.join(f"0x{b:02X}" for b in byte_array) + " }"
        pyperclip.copy(array_str)
        messagebox.showinfo("Готово", "Массив скопирован в буфер обмена.")

    def paste_from_clipboard(self):
        try:
            text = pyperclip.paste()
            self.parse_and_draw(text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить из буфера: {e}")

    def load_from_text(self):
        text = self.text_output.get("1.0", tk.END)
        try:
            self.parse_and_draw(text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный формат: {e}")

    def parse_and_draw(self, text):
        import re
        matches = re.findall(r'0x([0-9A-Fa-f]{2})', text)
        if len(matches) != 8:
            raise ValueError("Нужно 8 байт!")

        bytes_data = [int(b, 16) for b in matches]
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                bit = (bytes_data[x] >> (7 - y)) & 1
                self.cells[y][x] = bit
        self.draw_grid()
        self.update_text_output()

    def clear_grid(self):
        self.cells = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.draw_grid()
        self.update_text_output()

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelEditor(root)
    root.mainloop()
