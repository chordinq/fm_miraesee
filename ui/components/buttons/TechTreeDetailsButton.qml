import QtQuick
import QtQuick.Layouts
import ui 1.0

Item {
	id: root

	property string mode: "upgrade"
	property string topText: ""
	property string bottomText: ""
	property string skipLocId: "27999994002468864"
	property string skipLocTable: "General"
	property string claimLocId: "27937469076533248"
	property string claimLocTable: "General"
	property url topIconSource: Qt.resolvedUrl("../../../assets/sprites/General/Icons.png")
	property int topIconIndex: 29
	property url bottomIconSource: Qt.resolvedUrl("../../../assets/sprites/Currency/techPotions.png")
	property color fillColor: Theme.blue
	property bool enabled: true
	property real scaleW: 3.5
	property real scaleH: 2

	signal clicked()

	readonly property real baseSize: 128
	readonly property real bakedWidth: baseSize * scaleW
	readonly property real bakedHeight: baseSize * scaleH
	readonly property bool isUpgradeMode: root.mode === "upgrade"
	readonly property bool isSkipMode: root.mode === "skip"
	readonly property bool isClaimMode: root.mode === "claim"
	readonly property real rowIconScale: 25 / 64
	readonly property real topFontScale: 10 / 32
	readonly property real bottomFontScale: 11 / 32

	implicitWidth: bakedWidth
	implicitHeight: bakedHeight

	Item {
		id: canvas
		width: root.bakedWidth
		height: root.bakedHeight
		transformOrigin: Item.TopLeft
		transform: Scale {
			xScale: root.width / canvas.width
			yScale: root.height / canvas.height
		}

		RectRoundButton {
			anchors.fill: parent
			scaleW: root.scaleW
			scaleH: root.scaleH
			fillColor: root.fillColor
		}

		MouseArea {
			anchors.fill: parent
			enabled: root.enabled
			onClicked: root.clicked()
		}

		RowLayout {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter
			anchors.verticalCenterOffset: -canvas.height * 0.18
			spacing: canvas.height * 0.04
			visible: root.isUpgradeMode

			Item {
				width: canvas.height * root.rowIconScale
				height: width
				Layout.alignment: Qt.AlignVCenter

				SpriteSheet {
					anchors.fill: parent
					source: root.topIconSource
					spriteIndex: root.topIconIndex
				}
			}

			AppText {
				text: root.topText
				pixelSize: canvas.height * root.topFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}
		}

		AppText {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter
			anchors.verticalCenterOffset: -canvas.height * 0.18
			visible: root.isSkipMode
			locId: root.skipLocId
			locTable: root.skipLocTable
			pixelSize: canvas.height * root.topFontScale
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}

		AppText {
			anchors.centerIn: parent
			visible: root.isClaimMode
			locId: root.claimLocId
			locTable: root.claimLocTable
			pixelSize: canvas.height * root.topFontScale
			fillColor: Theme.white
			outlineColor: Theme.black
			outlineWeight: 8
		}

		RowLayout {
			anchors.horizontalCenter: parent.horizontalCenter
			anchors.verticalCenter: parent.verticalCenter
			anchors.verticalCenterOffset: canvas.height * 0.14
			spacing: canvas.height * 0.04
			visible: !root.isClaimMode

			Item {
				width: canvas.height * root.rowIconScale
				height: width
				Layout.alignment: Qt.AlignVCenter

				Image {
					anchors.fill: parent
					source: root.bottomIconSource
					fillMode: Image.PreserveAspectFit
					smooth: true
					mipmap: true
				}
			}

			AppText {
				text: root.bottomText
				pixelSize: canvas.height * root.bottomFontScale
				fillColor: Theme.white
				outlineColor: Theme.black
				outlineWeight: 8
				Layout.alignment: Qt.AlignVCenter
			}
		}
	}
}
