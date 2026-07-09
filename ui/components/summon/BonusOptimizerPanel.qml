pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0
import TMPText 1.0

Item {
	id: root

	property var summonController: null

	readonly property string locTable: "Miraesee"
	readonly property string titleLocId: "1000000000000004"
	readonly property string budgetLocId: "1000000000000005"
	readonly property string bonusLocId: "1000000000000006"
	readonly property string totalLocId: "1000000000000007"
	readonly property string routeLocId: "1000000000000008"
	readonly property string optimizeLocId: "1000000000000009"

	readonly property int budget: root.summonController ? root.summonController.optimizeBudget : 30
	readonly property bool resultReady: root.summonController ? root.summonController.optimizeReady : false
	readonly property int bonusCount: root.summonController ? root.summonController.optimizeBonus : 0
	readonly property int totalPulls: root.summonController ? root.summonController.optimizeTotal : 0
	readonly property var routeSegments: root.summonController ? root.summonController.optimizeRouteSegments : []

	readonly property real padH: Math.max(8, width * 0.06)
	readonly property real padV: Math.max(6, height * 0.028)
	readonly property real secGap: Math.max(5, height * 0.022)
	readonly property real labelPx: Math.max(11, height * 0.024)
	readonly property real valuePx: Math.max(14, height * 0.032)

	readonly property real btnScaleW: 4.5
	readonly property real btnScaleH: 1.0
	readonly property real btnH: Math.min(
		height * 0.085,
		(width - 2 * padH) / btnScaleW
	)

	readonly property int routeColumns: 8
	readonly property int routeRowCount: Math.ceil(routeSegments.length / routeColumns)
	readonly property real routeColSpacing: Math.max(4, width * 0.012)
	readonly property real routeRowSpacing: Math.max(4, height * 0.01)
	readonly property real routeCellW: routeFlickable.width > 0
		? (routeFlickable.width - routeColSpacing * (routeColumns - 1)) / routeColumns
		: 0
	readonly property real routeCellPx: Math.max(12, Math.min(18, routeCellW * 0.48))

	function localizedLabel(locId: string): string {
		UiLocale.selectedCode
		return TmpTextBridge.localized_text_table(
			locId,
			UiLocale.selectedCode,
			root.locTable
		)
	}

	function commitBudgetInput() {
		if (!root.summonController)
			return
		let v = parseInt(inputField.text)
		if (!isNaN(v) && v >= 1)
			root.summonController.setOptimizeBudget(v)
	}

	RectRounded {
		anchors.fill: parent
		fillColor: Theme.lightGrey
		scaleW: 50
		scaleH: 50
	}

	TMPText {
		id: titleText

		anchors.top: parent.top
		anchors.topMargin: root.padV
		anchors.horizontalCenter: parent.horizontalCenter
		tmpText: root.localizedLabel(root.titleLocId)
		pixelSize: root.labelPx * 1.05
		fillColor: Theme.black
		outlineWeight: 0
		horizontalAlignment: Text.AlignHCenter
	}

	Rectangle {
		id: div1

		anchors.top: titleText.bottom
		anchors.topMargin: root.secGap * 0.5
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		height: 1
		color: Theme.white
		opacity: 0.15
	}

	Item {
		id: budgetRow

		anchors.top: div1.bottom
		anchors.topMargin: root.secGap
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		height: root.valuePx * 1.9

		TMPText {
			anchors.left: parent.left
			anchors.verticalCenter: parent.verticalCenter
			tmpText: root.localizedLabel(root.budgetLocId)
			pixelSize: root.labelPx
			fillColor: Theme.black
			outlineWeight: 0
		}

		Rectangle {
			id: inputBg

			anchors.right: parent.right
			anchors.verticalCenter: parent.verticalCenter
			width: root.valuePx * 4.5
			height: parent.height * 0.82
			radius: height * 0.25
			color: Qt.darker(Theme.darkBlue, 1.5)
			border.color: inputField.activeFocus ? Theme.blue : Theme.checkBoxActiveGrey
			border.width: 1

			TextInput {
				id: inputField

				anchors {
					fill: parent
					leftMargin: 8
					rightMargin: 8
				}
				verticalAlignment: TextInput.AlignVCenter
				horizontalAlignment: TextInput.AlignHCenter
				text: root.budget.toString()
				color: Theme.white
				font.family: Theme.latinFontFamily
				font.pixelSize: root.valuePx
				font.bold: true
				inputMethodHints: Qt.ImhDigitsOnly
				validator: IntValidator { bottom: 1; top: 9999 }
				selectByMouse: true

				onEditingFinished: root.commitBudgetInput()

				onActiveFocusChanged: {
					if (!activeFocus)
						root.commitBudgetInput()
				}

				Binding on text {
					when: !inputField.activeFocus
					value: root.budget.toString()
				}
			}
		}
	}

	RectRoundButton {
		id: optimizeBtn

		anchors.top: budgetRow.bottom
		anchors.topMargin: root.secGap
		anchors.horizontalCenter: parent.horizontalCenter
		height: root.btnH
		scaleW: root.btnScaleW
		scaleH: root.btnScaleH
		labelText: root.localizedLabel(root.optimizeLocId).toUpperCase()
		labelScale: 0.3
		fillColor: Theme.blue
		buttonEnabled: root.summonController !== null
		onClicked: {
			if (!root.summonController)
				return
			inputField.focus = false
			root.commitBudgetInput()
			root.summonController.runOptimize()
		}
	}

	Rectangle {
		id: div2

		visible: root.resultReady
		anchors.top: optimizeBtn.bottom
		anchors.topMargin: root.secGap
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		height: 1
		color: Theme.white
		opacity: 0.15
	}

	Item {
		id: resultRow

		visible: root.resultReady
		anchors.top: div2.bottom
		anchors.topMargin: root.secGap
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		height: root.valuePx * 2.5

		Item {
			id: bonusCol

			anchors.left: parent.left
			anchors.top: parent.top
			anchors.bottom: parent.bottom
			width: parent.width * 0.45

			TMPText {
				id: bonusLabel

				anchors.left: parent.left
				anchors.top: parent.top
				tmpText: root.localizedLabel(root.bonusLocId)
				pixelSize: root.labelPx * 0.9
				fillColor: Theme.black
				outlineWeight: 0
			}

			TMPText {
				anchors.left: parent.left
				anchors.top: bonusLabel.bottom
				anchors.topMargin: root.secGap * 0.25
				tmpText: "+" + root.bonusCount.toString()
				pixelSize: root.valuePx * 1.1
				fillColor: root.bonusCount > 0 ? Theme.lightGreen : Theme.darkGrey
				outlineWeight: 0
			}
		}

		Rectangle {
			anchors.centerIn: parent
			width: 1
			height: parent.height * 0.7
			color: Theme.white
			opacity: 0.15
		}

		Item {
			id: totalCol

			anchors.right: parent.right
			anchors.top: parent.top
			anchors.bottom: parent.bottom
			width: parent.width * 0.45

			TMPText {
				id: totalLabel

				anchors.left: parent.left
				anchors.top: parent.top
				tmpText: root.localizedLabel(root.totalLocId)
				pixelSize: root.labelPx * 0.9
				fillColor: Theme.black
				outlineWeight: 0
			}

			TMPText {
				anchors.left: parent.left
				anchors.top: totalLabel.bottom
				anchors.topMargin: root.secGap * 0.25
				tmpText: root.totalPulls.toString()
				pixelSize: root.valuePx * 1.1
				fillColor: Theme.black
				outlineWeight: 0
			}
		}
	}

	Item {
		id: routeSection

		visible: root.resultReady
		anchors.top: resultRow.bottom
		anchors.topMargin: root.secGap
		anchors.left: parent.left
		anchors.leftMargin: root.padH
		anchors.right: parent.right
		anchors.rightMargin: root.padH
		anchors.bottom: parent.bottom
		anchors.bottomMargin: root.padV

		TMPText {
			id: routeLabel

			anchors.top: parent.top
			anchors.left: parent.left
			tmpText: root.localizedLabel(root.routeLocId)
			pixelSize: root.labelPx * 0.9
			fillColor: Theme.black
			outlineWeight: 0
		}

		Flickable {
			id: routeFlickable

			anchors.top: routeLabel.bottom
			anchors.topMargin: root.secGap * 0.35
			anchors.left: parent.left
			anchors.right: parent.right
			anchors.bottom: parent.bottom
			clip: true
			contentHeight: routeList.contentHeight
			boundsBehavior: Flickable.StopAtBounds

			ListView {
				id: routeList

				width: parent.width
				height: contentHeight
				interactive: false
				spacing: root.routeRowSpacing
				model: root.routeRowCount

				delegate: Row {
					id: routeRow

					required property int index

					spacing: root.routeColSpacing
					width: routeList.width
					height: root.routeCellPx * 1.35

					Repeater {
						model: root.routeColumns

						delegate: Item {
							id: routeCell

							required property int index

							readonly property int segIndex: routeRow.index * root.routeColumns + index
							readonly property bool hasSegment: segIndex < root.routeSegments.length
							readonly property bool hasNextSegment: hasSegment && segIndex < root.routeSegments.length - 1

							visible: hasSegment
							width: root.routeCellW
							height: routeRow.height

							Row {
								anchors.centerIn: parent
								spacing: Math.max(1, root.routeCellPx * 0.12)

								Text {
									text: routeCell.hasSegment ? root.routeSegments[routeCell.segIndex] : ""
									color: Theme.ghost
									font.family: Theme.latinFontFamily
									font.pixelSize: root.routeCellPx
									font.bold: true
								}

								Text {
									visible: routeCell.hasNextSegment
									text: "→"
									color: Theme.ghost
									opacity: 0.7
									font.family: Theme.latinFontFamily
									font.pixelSize: root.routeCellPx * 0.82
									font.bold: true
								}
							}
						}
					}
				}
			}
		}
	}
}
