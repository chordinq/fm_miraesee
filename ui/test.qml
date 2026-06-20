import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "SummonButton test (x" + testSummonCount + ", cost " + testSummonCost + ")"
	color: "#888888"

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	SummonButton {
		anchors.centerIn: parent
		summonCount: testSummonCount
		cost: testSummonCost
		onClicked: console.log("SummonButton clicked")
	}
}
