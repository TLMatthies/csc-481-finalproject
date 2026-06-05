from __future__ import annotations

import argparse
import re
import tkinter as tk
from tkinter import font, scrolledtext, ttk
from typing import Callable

from chat_controller import ChatController, KBToolCall


class ChatGui:
    def __init__(self, controller: ChatController) -> None:
        self.controller = controller
        self.table_widgets: list[tk.Widget] = []
        self.query_widgets: list[tk.Widget] = []

        self.root = tk.Tk()
        self.root.title(f"Dance Bot")
        self.root.geometry("860x720")
        self.root.minsize(560, 480)

        self.colors = {
            "bg": "#eef2f5",
            "panel": "#f8fafc",
            "user": "#2563eb",
            "assistant": "#ffffff",
            "text": "#111827",
            "muted": "#64748b",
            "border": "#d6dee8",
            "code_bg": "#111827",
            "code_text": "#e5e7eb",
        }

        self._configure_style()
        self._build_ui()
        self._poll_pending()

    def run(self) -> None:
        self.root.mainloop()

    def _configure_style(self) -> None:
        self.root.configure(bg=self.colors["bg"])
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(
            "TButton",
            background=self.colors["panel"],
            foreground=self.colors["text"],
            bordercolor=self.colors["border"],
            focusthickness=0,
            padding=(12, 8),
        )
        style.map("TButton", background=[("active", "#e2e8f0")])
        style.configure(
            "Send.TButton",
            background=self.colors["user"],
            foreground="#ffffff",
            bordercolor=self.colors["user"],
        )
        style.map("Send.TButton", background=[("active", "#1d4ed8")])

    def _build_ui(self) -> None:
        header = tk.Frame(self.root, bg=self.colors["panel"], height=54)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text=self.controller.model,
            bg=self.colors["panel"],
            fg=self.colors["text"],
            font=("TkDefaultFont", 13, "bold"),
        )
        title.pack(side=tk.LEFT, padx=(18, 8))

        self.status = tk.Label(
            header,
            text="Ready",
            bg=self.colors["panel"],
            fg=self.colors["muted"],
            font=("TkDefaultFont", 10),
        )
        self.status.pack(side=tk.LEFT)

        ttk.Button(header, text="Clear", command=self._clear_chat).pack(
            side=tk.RIGHT, padx=14
        )

        self.chat = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg=self.colors["bg"],
            fg=self.colors["text"],
            borderwidth=0,
            highlightthickness=0,
            padx=18,
            pady=18,
            font=("TkDefaultFont", 11),
            insertbackground=self.colors["text"],
        )
        self.chat.pack(fill=tk.BOTH, expand=True)
        self._configure_text_tags()

        input_bar = tk.Frame(self.root, bg=self.colors["panel"])
        input_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.entry = tk.Text(
            input_bar,
            height=3,
            wrap=tk.WORD,
            bg="#ffffff",
            fg=self.colors["text"],
            borderwidth=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            highlightcolor=self.colors["user"],
            padx=10,
            pady=8,
            font=("TkDefaultFont", 11),
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(14, 8), pady=12)
        self.entry.bind("<Control-Return>", self._send_message)
        self.entry.bind("<Command-Return>", self._send_message)

        self.send_button = ttk.Button(
            input_bar,
            text="Send",
            style="Send.TButton",
            command=self._send_message,
        )
        self.send_button.pack(side=tk.RIGHT, padx=(0, 14), pady=12)

    def _configure_text_tags(self) -> None:
        base = font.nametofont("TkDefaultFont")
        h1 = base.copy()
        h1.configure(size=17, weight="bold")
        h2 = base.copy()
        h2.configure(size=14, weight="bold")
        h3 = base.copy()
        h3.configure(size=12, weight="bold")
        bold = base.copy()
        bold.configure(weight="bold")
        italic = base.copy()
        italic.configure(slant="italic")
        code = font.Font(family="TkFixedFont", size=10)

        self.chat.tag_configure("user", justify=tk.RIGHT, lmargin1=90, lmargin2=90)
        self.chat.tag_configure("assistant", justify=tk.LEFT, rmargin=90)
        self.chat.tag_configure(
            "user_bubble",
            background=self.colors["user"],
            foreground="#ffffff",
            spacing1=8,
            spacing3=8,
            lmargin1=90,
            lmargin2=90,
            rmargin=16,
        )
        self.chat.tag_configure(
            "assistant_bubble",
            background=self.colors["assistant"],
            foreground=self.colors["text"],
            spacing1=8,
            spacing3=8,
            lmargin1=16,
            lmargin2=16,
            rmargin=90,
        )
        self.chat.tag_configure("name", foreground=self.colors["muted"], spacing1=12)
        self.chat.tag_configure("h1", font=h1, spacing1=8, spacing3=4)
        self.chat.tag_configure("h2", font=h2, spacing1=7, spacing3=3)
        self.chat.tag_configure("h3", font=h3, spacing1=6, spacing3=3)
        self.chat.tag_configure("bold", font=bold)
        self.chat.tag_configure("italic", font=italic)
        self.chat.tag_configure(
            "inline_code",
            font=code,
            background="#e5e7eb",
            foreground="#0f172a",
        )
        self.chat.tag_configure(
            "code_block",
            font=code,
            background=self.colors["code_bg"],
            foreground=self.colors["code_text"],
            lmargin1=28,
            lmargin2=28,
            rmargin=104,
            spacing1=6,
            spacing3=6,
        )
        self.chat.tag_configure("bullet", lmargin1=28, lmargin2=48)
        self.chat.tag_configure(
            "table",
            font=code,
            background="#f1f5f9",
            foreground=self.colors["text"],
            lmargin1=28,
            lmargin2=28,
            rmargin=104,
            spacing1=5,
            spacing3=5,
        )

    def _send_message(self, event: tk.Event | None = None) -> str:
        message = self.entry.get("1.0", tk.END).strip()
        if not message:
            return "break"

        self.entry.delete("1.0", tk.END)
        self._append_user_message(message)
        self._set_busy(True)
        self.controller.send_message(message)
        return "break"

    def _poll_pending(self) -> None:
        for response in self.controller.get_responses():
            self._append_assistant_message(response.content, response.tool_calls)
            self._set_busy(False)
        self.root.after(100, self._poll_pending)

    def _set_busy(self, busy: bool) -> None:
        state = tk.DISABLED if busy else tk.NORMAL
        self.send_button.configure(state=state)
        self.entry.configure(state=state)
        self.status.configure(text="Thinking" if busy else "Ready")
        if not busy:
            self.entry.focus_set()

    def _clear_chat(self) -> None:
        self.controller.clear()
        for widget in self.table_widgets:
            widget.destroy()
        self.table_widgets.clear()
        for widget in self.query_widgets:
            widget.destroy()
        self.query_widgets.clear()
        self.chat.configure(state=tk.NORMAL)
        self.chat.delete("1.0", tk.END)
        self.chat.configure(state=tk.DISABLED)
        self._set_busy(False)

    def _append_user_message(self, message: str) -> None:
        self._with_chat_enabled(lambda: self._insert_user_message(message))

    def _insert_user_message(self, message: str) -> None:
        self.chat.insert(tk.END, "You\n", ("name", "user"))
        self.chat.insert(tk.END, f"{message}\n\n", ("user", "user_bubble"))
        self.chat.see(tk.END)

    def _append_assistant_message(
        self,
        message: str,
        tool_calls: tuple[KBToolCall, ...] = (),
    ) -> None:
        self._with_chat_enabled(
            lambda: self._insert_assistant_message(message, tool_calls)
        )

    def _insert_assistant_message(
        self,
        message: str,
        tool_calls: tuple[KBToolCall, ...],
    ) -> None:
        self.chat.insert(tk.END, "Assistant\n", ("name", "assistant"))
        if tool_calls:
            self._insert_query_dropdown(tool_calls, ("assistant", "assistant_bubble"))
        self._insert_markdown(message, ("assistant", "assistant_bubble"))
        self.chat.insert(tk.END, "\n")
        self.chat.see(tk.END)

    def _with_chat_enabled(self, callback: Callable[[], None]) -> None:
        self.chat.configure(state=tk.NORMAL)
        callback()
        self.chat.configure(state=tk.DISABLED)

    def _insert_query_dropdown(
        self,
        tool_calls: tuple[KBToolCall, ...],
        base_tags: tuple[str, ...],
    ) -> None:
        panel = tk.Frame(
            self.chat,
            bg="#ffffff",
            borderwidth=1,
            relief=tk.SOLID,
            highlightbackground=self.colors["border"],
            highlightthickness=1,
        )
        self.query_widgets.append(panel)

        details = tk.Frame(panel, bg="#ffffff")
        expanded = False

        toggle = tk.Button(
            panel,
            text=f"+ Queries ({len(tool_calls)})",
            anchor=tk.W,
            bg="#f8fafc",
            fg=self.colors["text"],
            activebackground="#e2e8f0",
            activeforeground=self.colors["text"],
            borderwidth=0,
            padx=10,
            pady=7,
            font=("TkDefaultFont", 10, "bold"),
        )
        toggle.pack(fill=tk.X)

        def set_expanded(is_expanded: bool) -> None:
            nonlocal expanded
            expanded = is_expanded
            if expanded:
                details.pack(fill=tk.X, padx=8, pady=(0, 8))
                toggle.configure(text=f"- Queries ({len(tool_calls)})")
            else:
                details.pack_forget()
                toggle.configure(text=f"+ Queries ({len(tool_calls)})")

        toggle.configure(command=lambda: set_expanded(not expanded))

        for index, call in enumerate(tool_calls, start=1):
            self._add_query_detail(details, f"Query {index}", call.query)
            self._add_query_detail(details, f"Response {index}", call.response)

        self.chat.insert(tk.END, "\n", base_tags)
        self.chat.window_create(tk.END, window=panel, padx=28, pady=6)
        self.chat.insert(tk.END, "\n", base_tags)

    def _add_query_detail(self, parent: tk.Widget, title: str, body: str) -> None:
        tk.Label(
            parent,
            text=title,
            anchor=tk.W,
            bg="#ffffff",
            fg=self.colors["text"],
            font=("TkDefaultFont", 10, "bold"),
            pady=4,
        ).pack(fill=tk.X)

        tk.Label(
            parent,
            text=body,
            anchor=tk.NW,
            justify=tk.LEFT,
            bg=self.colors["code_bg"],
            fg=self.colors["code_text"],
            font=("TkFixedFont", 10),
            padx=9,
            pady=7,
            wraplength=660,
        ).pack(fill=tk.X, pady=(0, 8))

    def _insert_markdown(self, markdown: str, base_tags: tuple[str, ...]) -> None:
        in_code_block = False
        code_lines: list[str] = []
        lines = markdown.splitlines()
        index = 0

        while index < len(lines):
            raw_line = lines[index]
            line = raw_line.rstrip()
            if line.strip().startswith("```"):
                if in_code_block:
                    self.chat.insert(
                        tk.END,
                        "\n".join(code_lines).rstrip() + "\n",
                        (*base_tags, "code_block"),
                    )
                    code_lines = []
                    in_code_block = False
                else:
                    in_code_block = True
                index += 1
                continue

            if in_code_block:
                code_lines.append(raw_line)
                index += 1
                continue

            if self._is_table_start(lines, index):
                table_lines: list[str] = []
                while index < len(lines) and self._is_table_line(lines[index]):
                    table_lines.append(lines[index].rstrip())
                    index += 1
                self._insert_table(table_lines, base_tags)
                continue

            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
            numbered = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
            horizontal_rule = re.match(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$", line)

            if heading:
                level = len(heading.group(1))
                tag = "h1" if level == 1 else "h2" if level == 2 else "h3"
                self._insert_inline_markdown(heading.group(2), (*base_tags, tag))
                self.chat.insert(tk.END, "\n", base_tags)
            elif horizontal_rule:
                self.chat.insert(tk.END, "\n", base_tags)
            elif bullet:
                self.chat.insert(tk.END, "- ", (*base_tags, "bullet"))
                self._insert_inline_markdown(bullet.group(1), (*base_tags, "bullet"))
                self.chat.insert(tk.END, "\n", base_tags)
            elif numbered:
                self.chat.insert(tk.END, f"{numbered.group(1)}. ", (*base_tags, "bullet"))
                self._insert_inline_markdown(numbered.group(2), (*base_tags, "bullet"))
                self.chat.insert(tk.END, "\n", base_tags)
            else:
                self._insert_inline_markdown(line, base_tags)
                self.chat.insert(tk.END, "\n", base_tags)
            index += 1

        if in_code_block and code_lines:
            self.chat.insert(
                tk.END,
                "\n".join(code_lines).rstrip() + "\n",
                (*base_tags, "code_block"),
            )

    def _is_table_start(self, lines: list[str], index: int) -> bool:
        if index + 1 >= len(lines):
            return False
        return self._is_table_line(lines[index]) and self._is_table_separator(
            lines[index + 1]
        )

    @staticmethod
    def _is_table_line(line: str) -> bool:
        stripped = line.strip()
        return stripped.count("|") >= 2

    @staticmethod
    def _is_table_separator(line: str) -> bool:
        if not ChatGui._is_table_line(line):
            return False
        cells = ChatGui._split_table_row(line)
        return all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)

    @staticmethod
    def _split_table_row(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    def _insert_table(self, table_lines: list[str], base_tags: tuple[str, ...]) -> None:
        rows = [
            [self._plain_markdown(cell) for cell in self._split_table_row(line)]
            for line in table_lines
            if not self._is_table_separator(line)
        ]
        if not rows:
            return

        column_count = max(len(row) for row in rows)
        for row in rows:
            row.extend([""] * (column_count - len(row)))

        table = tk.Frame(
            self.chat,
            bg=self.colors["border"],
            borderwidth=1,
            relief=tk.SOLID,
        )
        self.table_widgets.append(table)

        for column in range(column_count):
            table.grid_columnconfigure(column, weight=1, uniform="table")

        for row_index, row in enumerate(rows):
            for column_index, cell in enumerate(row):
                is_header = row_index == 0
                background = "#e2e8f0" if is_header else "#ffffff"
                if row_index > 0 and row_index % 2 == 0:
                    background = "#f8fafc"

                label = tk.Label(
                    table,
                    text=cell,
                    anchor=tk.NW,
                    justify=tk.LEFT,
                    bg=background,
                    fg=self.colors["text"],
                    font=("TkDefaultFont", 10, "bold" if is_header else "normal"),
                    padx=10,
                    pady=8,
                    wraplength=max(120, 520 // column_count),
                )
                label.grid(
                    row=row_index,
                    column=column_index,
                    sticky=tk.NSEW,
                    padx=(0, 1),
                    pady=(0, 1),
                )

        self.chat.insert(tk.END, "\n", base_tags)
        self.chat.window_create(tk.END, window=table, padx=28, pady=8)
        self.chat.insert(tk.END, "\n", base_tags)

    @staticmethod
    def _plain_markdown(text: str) -> str:
        text = re.sub(r"`([^`]+)`", r"\1", text)
        text = re.sub(r"\*\*([^*]+)\*\*|__([^_]+)__", lambda m: m.group(1) or m.group(2), text)
        text = re.sub(r"\*([^*]+)\*|_([^_]+)_", lambda m: m.group(1) or m.group(2), text)
        return text

    def _insert_inline_markdown(self, text: str, base_tags: tuple[str, ...]) -> None:
        token_pattern = re.compile(r"(`[^`]+`|\*\*[^*]+\*\*|__[^_]+__|\*[^*]+\*|_[^_]+_)")
        cursor = 0

        for match in token_pattern.finditer(text):
            if match.start() > cursor:
                self.chat.insert(tk.END, text[cursor : match.start()], base_tags)

            token = match.group(0)
            if token.startswith("`"):
                self.chat.insert(tk.END, token[1:-1], (*base_tags, "inline_code"))
            elif token.startswith(("**", "__")):
                self.chat.insert(tk.END, token[2:-2], (*base_tags, "bold"))
            else:
                self.chat.insert(tk.END, token[1:-1], (*base_tags, "italic"))
            cursor = match.end()

        if cursor < len(text):
            self.chat.insert(tk.END, text[cursor:], base_tags)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chat with an Ollama model.")
    parser.add_argument("--model", default="gemma4:e2b")
    parser.add_argument("--system-prompt", default=None)
    parser.add_argument("--no-thinking", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    controller = ChatController(
        model=args.model,
        system_prompt=args.system_prompt,
        thinking=not args.no_thinking,
    )
    ChatGui(controller).run()


if __name__ == "__main__":
    main()
