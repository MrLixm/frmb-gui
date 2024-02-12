from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets


class TextOverlayWidget(QtWidgets.QFrame):
    """
    An overlay covering its parent widget to display a centered message.

    The overlay can be styled as a regular widget using the
    ``QFrame.TextOverlayWidget`` selector.

    Example::

        QFrame.TextOverlayWidget {
            background-color: rgba(150,0,0,100);
            color: white;
            /*control the shadow color*/
            alternate-background-color: black;
        }

    Args:
        text: the message to display
    """

    def __init__(self, text: str, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent=parent)
        self._text: str = text
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def set_text(self, new_text: str):
        """
        Change the message displayed on the widget.
        """
        self._text = new_text
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        qpainter = QtGui.QPainter(self)
        qstyleoption = QtWidgets.QStyleOption()
        qstyleoption.initFrom(self)

        style: QtWidgets.QStyle = self.style()
        rect: QtCore.QRect = self.rect()

        style.drawPrimitive(QtWidgets.QStyle.PE_Widget, qstyleoption, qpainter, self)

        # we create a second painter to isolate the text
        text_pixmap = QtGui.QPixmap(rect.width(), rect.height())
        text_pixmap.fill(QtCore.Qt.GlobalColor.transparent)
        qpainter2 = QtGui.QPainter(text_pixmap)
        qpainter2.setFont(self.font())

        style.drawItemText(
            qpainter2,
            rect,
            QtCore.Qt.AlignmentFlag.AlignCenter,
            self.palette(),
            True,
            self._text,
            QtGui.QPalette.ColorRole.Text,
        )
        qpainter2.end()

        # glow/shadow effect on text

        shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self)
        background_color: QtGui.QColor = self.palette().alternateBase().color()
        shadow_effect.setColor(background_color)
        shadow_effect.setOffset(0, 0)
        shadow_effect.setBlurRadius(40)

        graphic_scene = QtWidgets.QGraphicsScene()
        graphic_item = QtWidgets.QGraphicsPixmapItem(text_pixmap)
        graphic_item.setGraphicsEffect(shadow_effect)
        graphic_scene.addItem(graphic_item)
        graphic_scene.render(qpainter)
