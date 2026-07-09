pragma Singleton
import QtQuick

QtObject {
	property real aspectW: 3.65
	property real aspectH: 1.75
	readonly property real aspect: aspectW / aspectH
}
