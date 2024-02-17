import sys
from pathlib import Path
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets


class SearchableComboBox(QtWidgets.QComboBox):
    """
    An editable combobox where typing text will display suggestion of available items.

    SRC: https://stackoverflow.com/a/24456461
    """

    def __init__(self, parent=None):
        super(SearchableComboBox, self).__init__(parent)

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setEditable(True)
        self.setInsertPolicy(self.InsertPolicy.NoInsert)

        # 1. Create
        self.filterProxyModel = QtCore.QSortFilterProxyModel(self)
        self.completer = QtWidgets.QCompleter(self)

        # 2. Add
        self.setCompleter(self.completer)

        # 3. Modify
        self.filterProxyModel.setFilterCaseSensitivity(
            QtCore.Qt.CaseSensitivity.CaseInsensitive
        )
        self.filterProxyModel.setSourceModel(self.model())
        self.completer.setModel(self.filterProxyModel)
        # completions are displayed in a popup window
        self.completer.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)

        # 4. Connections
        self.lineEdit().editingFinished.connect(self.onEditingFinished)
        self.lineEdit().textEdited[str].connect(
            self.filterProxyModel.setFilterFixedString
        )
        self.completer.activated[str].connect(self.onCompleterActivated)

    def onEditingFinished(self):
        """
        Called when line-edit loose focus or enter/return is pressed.

        We check if the current text correpond to one of the available text and if not
        we just reset it to the previously selected one.
        """
        itemIndex = self.findText(self.lineEdit().text())
        if itemIndex == -1:
            itemIndex = self.currentIndex()

        self.setCurrentIndex(itemIndex)
        return

    def onCompleterActivated(self, text):
        """
        On selection of an item from the completer, select the corresponding item from combobox
        :param text:
        :return:
        """
        if not text:
            return

        index = self.findText(text)
        self.setCurrentIndex(index)
        text = self.itemText(index)
        self.currentTextChanged[str].emit(text)
        self.currentIndexChanged[int].emit(index)
        self.activated[int].emit(text)
        return

    def setModel(self, model):
        """
        on model change, update the models of the filter and completer as well
        :param model:
        :return:
        """
        super(SearchableComboBox, self).setModel(model)
        self.filterProxyModel.setSourceModel(model)
        self.completer.setModel(self.filterProxyModel)

    def setModelColumn(self, column):
        """
        on model column change, update the model column of the filter and completer as well
        :param column:
        :return:
        """
        self.completer.setCompletionColumn(column)
        self.filterProxyModel.setFilterKeyColumn(column)
        super(SearchableComboBox, self).setModelColumn(column)


class FontWeightListWidget(QtWidgets.QWidget):
    def __init__(
        self,
        weights: list[int],
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent)
        text = "Azerty WEIGHT|weight "

        self.layout_main = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout_main)

        for weight in weights:

            label = QtWidgets.QLabel(f"{text} {weight}")
            label.setProperty("weight", str(weight))
            self.layout_main.addWidget(label)


class FontPreview(QtWidgets.QFrame):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

        weights = [
            0,
            100,
            200,
            300,
            400,
            500,
            600,
            700,
            800,
        ]

        # 1. create
        self.layout_main = QtWidgets.QVBoxLayout()
        self.layout_column = QtWidgets.QHBoxLayout()
        self.font_name_field = SearchableComboBox()
        self.weight_widget1 = FontWeightListWidget(weights)

        # 2. build layout
        self.setLayout(self.layout_main)
        self.layout_main.addWidget(self.font_name_field)
        self.layout_main.addLayout(self.layout_column)
        self.layout_main.addStretch(1)
        self.layout_column.addWidget(self.weight_widget1)

        # 3. modify
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.font_name_field.addItems(QtGui.QFontDatabase.families())
        self.font_name_field.setCurrentText("TASA Explorer")

        # 4. connect
        self.font_name_field.currentTextChanged.connect(self._on_lineedit)
        self.reload_stylesheet()

    def _on_lineedit(self):
        self.reload_stylesheet()

    def reload_stylesheet(self):
        self.setStyleSheet(
            f"""
        QWidget.FontPreview {{
            padding: 30px;
        }}
        QLabel {{font-family: {self.font_name_field.currentText()}, Comic Sans MS; font-size: 40pt;}}
        QLabel[weight="0"] {{ font-weight: 0; }}
        QLabel[weight="100"] {{ font-weight: 100; }}
        QLabel[weight="200"] {{ font-weight: 200; }}
        QLabel[weight="300"] {{ font-weight: 300; }}
        QLabel[weight="400"] {{ font-weight: 400; }}
        QLabel[weight="500"] {{ font-weight: 500; }}
        QLabel[weight="600"] {{ font-weight: 600; }}
        QLabel[weight="700"] {{ font-weight: 700; }}
        QLabel[weight="800"] {{ font-weight: 800; }}
        
        """
        )


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.main_widget = FontPreview()
        self.setCentralWidget(self.main_widget)


def main():
    app = QtWidgets.QApplication()

    fonts = list(Path(r"F:\softwares\fonts\Intel-One-Mono\1.3.0\ttf").glob("*.ttf"))
    fonts += list(Path(r"F:\softwares\fonts\Geist\Geist").glob("*.otf"))
    for font_path in fonts:
        fontid = QtGui.QFontDatabase.addApplicationFont(str(font_path))
        names = QtGui.QFontDatabase.applicationFontFamilies(fontid)
        styles = QtGui.QFontDatabase.styles(names[0])
        print(f"{font_path.name:<40} {str(names):<30} {styles}")

    window = MainWindow()

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
