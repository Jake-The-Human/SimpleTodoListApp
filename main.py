
import tkinter.scrolledtext as tkscrolled
import tkinter as tk
import re  # regular expressions
import json

DONE = " (DONE)\n"
DKM_BACKGROUND, DKM_FONT_COLOR = "black", "white"
FONT_SIZE, FONT_TYPE = 12, "Helvetica"
TO_DO_LIST_FILE_NAME = "todo.json"


class Application(tk.Frame):
    def __init__(self, master=None):
        if master is None:
            master = tk.Tk()

        super().__init__(master)

        self.pack(fill="both", expand=True)

        self.master = master
        self.master.title("To Do List")

        self.master.bind(
            "<Control-s>",
            lambda event: self.saveList(setTimer=False)
        )
        self.master.bind(
            "<Control-q>",
            lambda event: self.quitApp()
        )
        self.master.bind(
            "<Escape>",
            lambda event: self.quitApp()
        )
        self.master.bind(
            "<KeyPress>",
            lambda event: self.syntaxCheck()
        )

        self.createWidgets()
        self.saveList()
        return

    def createWidgets(self):
        try:
            with open(TO_DO_LIST_FILE_NAME) as f:
                todoText = json.load(f)
        except IOError:
            with open(TO_DO_LIST_FILE_NAME, 'w+') as f:
                f.write('{}')
                todoText = json.load(f)

        self.fontSize = FONT_SIZE
        self.textBox = tkscrolled.ScrolledText(
            master=self,
            font=(FONT_TYPE, self.fontSize)
        )
        # Maybe some theme or something could be done with the code bellow
        # self.textBox.tag_config(
        #     "font_color",
        #     foreground="black"
        # )
        self.textBox.insert(
            tk.INSERT,
            self.parseJsonToText(todoText),
            'font_color'
        )
        # self.textBox.grid_propagate(False)
        self.textBox.pack(fill="both", expand=True)
        self.textBox.focus()

        self.syntaxCheck()
        return

    def saveList(self, setTimer=True):
        # Write out self.textBox to a file
        with open(TO_DO_LIST_FILE_NAME, 'w') as f:
            todoText = self.textBox.get("1.0", "end-1c")
            jsonFromText = self.parseTextToJson(todoText)
            todoJson = json.dumps(jsonFromText)
            f.write(todoJson)

        if setTimer:
            return self.master.after(1000, self.saveList)

    def quitApp(self):
        self.saveList(setTimer=False)
        self.master.destroy()
        return

    def syntaxCheck(self):
        def tagHelper(remove: str, add: str, start: str, end: str):
            self.textBox.tag_remove(remove, start, end)
            self.textBox.tag_add(add, start, end)
            return

        lines = self.textBox.get("1.0", "end-1c").split('\n')
        pattern = re.compile('(.*[(][Dd][Oo][Nn][Ee][)])')
        self.textBox.tag_configure("red", foreground="red")
        self.textBox.tag_configure("normal", foreground="black")
        # checks = {'#': False, '-': False, '\t-': False}
        # match = re.finditer(pattern, self.textBox.get("1.0", "end-1c"))
        for lineNumber, line in enumerate(lines, 1):
            match = re.search(pattern, line)
            lineNumberStr = str(lineNumber) + "."
            start = lineNumberStr + "0"
            if match is None and self.textBox.tag_names(start) != "normal":
                end = lineNumberStr + str(len(line))
                tagHelper(remove="red", add="normal", start=start, end=end)
            elif self.textBox.tag_names(start) != "red":
                end = lineNumberStr + str(match.end())
                tagHelper(remove="normal", add="red", start=start, end=end)
        return

    def parseJsonToText(self, jsonFile):
        text = ""
        for superTodo, subTodos in jsonFile.items():
            text += "# " + superTodo + '\n'
            for event in subTodos:
                if event == 'notes':
                    text += "Notes: " + jsonFile[superTodo][event] + "\n"
                else:
                    task = jsonFile[superTodo][event]
                    for name in task:
                        endOfLine = (DONE if (task[name]['done']) else "\n")
                        text += "- " + name + endOfLine
                        for subTask in task[name]['subtasks']:
                            text += "\t: " + subTask + "\n"
            text += '\n'
        return text

    def parseTextToJson(self, text):
        def eventParse(line):
            eventsDict = {}
            for event in line:
                subtasks = []
                if re.search('\t: ', event) is not None:
                    subtasks = event.split("\t:")
                    event = subtasks.pop(0).strip()
                    subtasks = [sub.strip() for sub in subtasks]

                foundDone = re.search(
                    '([(][Dd][Oo][Nn][Ee][)])', event) is not None
                event = event.replace(DONE, "")
                eventsDict[event.strip()] = {
                    'done': foundDone,
                    'subtasks': subtasks
                }
            return eventsDict

        textLines = text.split('#')
        textLines.pop(0)
        jsonFile = {}
        for text in textLines:
            day, *items = text.split('-')
            jsonFile[day.strip()] = {"events": eventParse(items)}

        return jsonFile


# Run app
if __name__ == "__main__":
    Application().mainloop()
