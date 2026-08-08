import ttkbootstrap as ttk
from ttkbootstrap.constants import PRIMARY

import pandas as pd

from ui.formatting import NUMERIC_COLUMNS, format_value, sort_key

STRIPE_TAG = "oddrow"
STRIPE_COLOR = "#eef1f6"


class FiiTable(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.df = pd.DataFrame()
        self._sort_column: str | None = None
        self._sort_reverse = False

        self.tree = ttk.Treeview(self, show="headings", bootstyle=PRIMARY)
        self.tree.tag_configure(STRIPE_TAG, background=STRIPE_COLOR)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview, bootstyle="round")
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview, bootstyle="round")
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def set_dataframe(self, df: pd.DataFrame):
        self.df = df.reset_index(drop=True).copy()
        self._sort_column = None
        self._sort_reverse = False
        self._rebuild_columns()
        self._populate()

    def _rebuild_columns(self):
        columns = list(self.df.columns)
        self.tree["columns"] = columns

        for col in columns:
            anchor = "e" if col in NUMERIC_COLUMNS else "w"
            self.tree.heading(col, text=col, anchor=anchor, command=lambda c=col: self._sort_by(c))
            width = 100 if col in NUMERIC_COLUMNS else 140
            self.tree.column(col, width=width, minwidth=60, anchor=anchor, stretch=False)

    def _populate(self):
        self.tree.delete(*self.tree.get_children())
        columns = list(self.df.columns)
        for i, (_, row) in enumerate(self.df.iterrows()):
            values = [format_value(col, row[col]) for col in columns]
            tags = (STRIPE_TAG,) if i % 2 == 1 else ()
            self.tree.insert("", "end", values=values, tags=tags)

    def _sort_by(self, column: str):
        if self.df.empty:
            return

        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        keys = self.df[column].map(lambda v: sort_key(column, v))
        self.df = (
            self.df.assign(__sort_key__=keys)
            .sort_values("__sort_key__", ascending=not self._sort_reverse, kind="mergesort")
            .drop(columns="__sort_key__")
            .reset_index(drop=True)
        )
        self._populate()
