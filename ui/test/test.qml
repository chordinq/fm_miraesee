import QtQuick
import QtQuick.Controls
import ui 1.0

ApplicationWindow {
	id: window

	width: initWinWidth
	height: initWinHeight
	visible: true
	title: "SummonButton test (x" + testSummonCount + ", cost " + testSummonCost + ")"
	color: Theme.darkBlue

	readonly property real summonAspect: 4 / 2

	readonly property real summonButtonWidth: Math.min(
		width * 0.55,
		height * 0.28 * summonAspect
	)

	readonly property real summonButtonHeight: summonButtonWidth / summonAspect

	Component.onCompleted: {
		Theme.language = uiLanguage
	}

	SummonButton {
		anchors.centerIn: parent
		width: window.summonButtonWidth
		height: window.summonButtonHeight
		summonCount: testSummonCount
		cost: testSummonCost
		onClicked: console.log("SummonButton clicked")
	}
}
