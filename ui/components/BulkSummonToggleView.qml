pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
	id: root

	property var summonController: null
	property real rowSpacingRatio: 0.04

	readonly property var countOptions: root.summonController
		? root.summonController.summonCountOptions
		: []
	readonly property int optionCount: root.countOptions.length
	readonly property real rowSpacing: root.optionCount > 1
		? height * root.rowSpacingRatio
		: 0
	readonly property real buttonHeight: root.optionCount > 0
		? (height - root.rowSpacing * (root.optionCount - 1)) / root.optionCount
		: 0
	readonly property real buttonWidth: root.buttonHeight * 2

	implicitWidth: buttonWidth
	implicitHeight: root.optionCount > 0
		? root.buttonHeight * root.optionCount + root.rowSpacing * (root.optionCount - 1)
		: 0

	Column {
		anchors.fill: parent
		spacing: root.rowSpacing

		Repeater {
			model: root.optionCount

			delegate: SummonCountButton {
				required property int index

				readonly property int sourceIndex: root.optionCount - 1 - index
				readonly property int countValue: root.countOptions[sourceIndex]

				width: root.buttonWidth
				height: root.buttonHeight
				summonCount: countValue
				selected: root.summonController
					&& root.summonController.summonCount === countValue
				onClicked: {
					if (root.summonController)
						root.summonController.setSummonCount(countValue)
				}
			}
		}
	}
}
