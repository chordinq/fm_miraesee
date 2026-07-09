pragma Singleton
import QtQuick

QtObject {
	property real scaleW: 3.65
	property real scaleH: 1.75
	readonly property real aspect: scaleW / scaleH
}
