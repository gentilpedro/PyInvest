import tkinter as tk
from tkinter import messagebox


def run():
    try:
        dy = float(entry_dy.get()) if entry_dy.get() else None
        pvp = float(entry_pvp.get()) if entry_pvp.get() else None

        print(f"DY >= {dy}, P/VP <= {pvp}")

        # chama teu use case aqui
        # use_case.execute(dy, pvp)

        messagebox.showinfo("Sucesso", "Processando dados...")

    except ValueError:
        messagebox.showerror("Erro", "Digite apenas números válidos!")

root = tk.Tk()
root.title("PyInvest")

tk.Label(root, text="DY mínimo").pack()
entry_dy = tk.Entry(root)
entry_dy.pack()

tk.Label(root, text="P/VP máximo").pack()
entry_pvp = tk.Entry(root)
entry_pvp.pack()

tk.Button(root, text="Analisar", command=run).pack()


root.mainloop()