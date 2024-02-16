import logging
from typing import Optional

from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtWidgets import QStyle

LOGGER = logging.getLogger(__name__)


class SwitchButton(QtWidgets.QAbstractButton):
    """
    A checkable button with a "switch" look: a box woth an inner handle moving left or right.

    **Styling**

    You can use the ``::item`` selector to style the inner handle.
    You must also set a min width/height on the box and the handle.

    .. code-block:: css

        QWidget.SwitchButton {
            background-color: green;
            max-width: 50px;
            min-height: 25px;
            border-radius: 12px;
            margin: 5px;
        }
        QWidget.SwitchButton::item {
            background-color: black;
            border-radius: 10px;
            min-width: 20px;
            min-height: 20px;
            margin: 5px;
        }


    Args:
        switch_speed: time it take to play the left<>right animation in ms.
        parent: usual QWidget parent.
    """

    def __init__(
        self,
        switch_speed: int = 150,
        parent: Optional[QtWidgets.QWidget] = None,
    ):
        super().__init__(parent=parent)

        self._position: float = 0.0
        """
        position of the cursor in 0-1 range
        """

        self._mouse_pressed: bool = False

        self.animation = QtCore.QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setPropertyName(b"position")
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(switch_speed)
        self.animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutExpo)

        self.setCheckable(True)
        self.setMinimumHeight(10)

        self.clicked.connect(self._on_press)

    @QtCore.Property(float)
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, new_position: float):
        self._position = new_position
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent):
        qpainter = QtGui.QPainter(self)
        qpainter.setRenderHint(qpainter.RenderHint.Antialiasing)

        qstyleoption = QtWidgets.QStyleOptionButton()
        qstyleoption_item = QtWidgets.QStyleOptionViewItem()

        qstyleoption.initFrom(self)
        qstyleoption_item.initFrom(self)

        state_check = (
            QStyle.StateFlag.State_On
            if self.isChecked()
            else QStyle.StateFlag.State_Off
        )
        state_press = QStyle.StateFlag.State_Sunken if self._mouse_pressed else None

        qstyleoption.state = qstyleoption.state | state_check
        qstyleoption_item.state = qstyleoption_item.state | state_check
        if state_press:
            qstyleoption.state = qstyleoption.state | state_press
            qstyleoption_item.state = qstyleoption_item.state | state_press

        # draw background
        self.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_Widget,
            qstyleoption,
            qpainter,
            self,
        )

        # the "background" might have margins
        bg_rect = self.style().subElementRect(
            QStyle.SubElement.SE_PushButtonContents,
            qstyleoption,
            self,
        )

        # retrieve cursor size from stylesheet
        cursor_size = self.style().sizeFromContents(
            QStyle.ContentsType.CT_ItemViewItem,
            qstyleoption_item,
            QtCore.QSize(self.height(), self.height()),
            self,
        )

        cursor_rect = QtCore.QRectF(0, 0, cursor_size.width(), cursor_size.height())
        # move item based on current position (this is a lerp operation)
        right_value = float(
            (1 - self._position) * (bg_rect.left() + cursor_rect.width())
            + self._position * bg_rect.right()
        )
        right_value += 0.5
        # not sure why we need it but else we have a visual offset
        cursor_rect.moveRight(right_value)
        cursor_rect.moveCenter(
            QtCore.QPointF(cursor_rect.center().x(), bg_rect.center().y() + 0.5)
        )

        qstyleoption_item.rect = cursor_rect.toAlignedRect()

        self.style().drawPrimitive(
            QStyle.PrimitiveElement.PE_PanelItemViewItem,
            qstyleoption_item,
            qpainter,
            self,
        )

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        super().mousePressEvent(event)
        self._mouse_pressed = True

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent):
        super().mouseReleaseEvent(event)
        self._mouse_pressed = False

    def _on_press(self, *args):
        self.animation.setDirection(
            self.animation.Direction.Forward
            if self.isChecked()
            else self.animation.Direction.Backward
        )
        self.animation.start()
