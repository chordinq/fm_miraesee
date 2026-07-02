import QtQuick
import QtQuick.Layouts
import ui 1.0
import TMPText 1.0

Item {
	id: root
	width: 720
	height: 480

	ColumnLayout {
		anchors.centerIn: parent
		spacing: 24

		TMPText {
			tmpText: TmpTextBridge.format_level_plus_one_text(41, UiLocale.selectedCode, 1)
			pixelSize: 32
			outlineWeight: 8
			Layout.alignment: Qt.AlignHCenter
		}

		TMPText {
			tmpText: TmpTextBridge.format_long_text(1342343)
			pixelSize: 28
			Layout.alignment: Qt.AlignHCenter
		}

		TMPText {
			tmpText: TmpTextBridge.format_currency_value_text(1500, 3)
			iconSource: TmpTextBridge.currency_icon_source(3)
			iconPixelSize: 28
			pixelSize: 28
			Layout.alignment: Qt.AlignHCenter
		}
	}
}
