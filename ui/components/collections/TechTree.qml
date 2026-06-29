pragma ComponentBehavior: Bound
import QtQuick
import ui 1.0

Item {
    id: root

    property var techTreeModel: null

    signal nodeClicked(var nodeModel)

    property real verticalGapRatio: 0.7
    property real horizontalGapRatio: 1.7
    property real iconCenterYRatio: 0.5
    property real iconSizeRatio: 0.22

    readonly property int iconLogicalSize: 256
    readonly property var layerRows: techTreeModel ? techTreeModel.layerRows : []

    readonly property int maxNodeCount: {
        var m = 0
        if (root.layerRows) {
            for (var i = 0; i < root.layerRows.length; i++) {
                if (root.layerRows[i].nodes && root.layerRows[i].nodes.length > m)
                    m = root.layerRows[i].nodes.length
            }
        }
        return m
    }

    readonly property real widthFitDenominator: maxNodeCount > 0
        ? (maxNodeCount + (maxNodeCount + 1) * horizontalGapRatio)
        : 0

    readonly property real exactIconSize: {
        if (width <= 0)
            return iconLogicalSize
        if (widthFitDenominator > 0)
            return width / widthFitDenominator
        return width * iconSizeRatio
    }
    readonly property real iconSize: exactIconSize
    readonly property real verticalGap: iconSize * verticalGapRatio
    readonly property real horizontalGap: iconSize * horizontalGapRatio
    readonly property real entryScale: iconSize / iconLogicalSize
    readonly property real lineWidth: 10 * entryScale
    readonly property real visualCenterY: iconSize * iconCenterYRatio

    function nodeFillColor(nodeModel) {
        if (!nodeModel)
            return Theme.white
        if (nodeModel.maxLevel)
            return Theme.lightGreen
        if (nodeModel.requirementsMet)
            return Theme.brown
        return Theme.white
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.white
    }

    Flickable {
        id: flickable

        anchors.fill: parent
        contentWidth: Math.max(width, treeColumn.width)
        contentHeight: Math.max(height, treeColumn.height)
        clip: true
        boundsBehavior: Flickable.StopAtBounds

        Column {
            id: treeColumn

            width: flickable.width
            spacing: 0

            Item {
                width: 1
                height: root.verticalGap
            }

            Repeater {
                model: root.layerRows

                delegate: Item {
                    id: layerRow

                    required property int index
                    required property var modelData

                    readonly property int layerIndex: index
                    readonly property var nodesInLayer: modelData.nodes
                    readonly property int nodeCount: nodesInLayer.length
                    
                    readonly property bool hasPrevLayer: layerIndex > 0
                    readonly property int prevCount: hasPrevLayer ? root.layerRows[layerIndex - 1].nodes.length : 0

                    readonly property bool hasNextLayer: layerIndex < root.layerRows.length - 1
                    readonly property int nextCount: hasNextLayer ? root.layerRows[layerIndex + 1].nodes.length : 0

                    readonly property real rowContentWidth: nodeCount * root.iconSize + Math.max(0, nodeCount - 1) * root.horizontalGap
                    readonly property real centerX: parent.width / 2
                    readonly property real startX: centerX - rowContentWidth / 2
                    readonly property real leftX: startX + root.iconSize / 2
                    readonly property real rightX: startX + Math.max(0, nodeCount - 1) * (root.iconSize + root.horizontalGap) + root.iconSize / 2

                    width: treeColumn.width
                    height: root.iconSize + (hasNextLayer ? root.verticalGap : 0)

                    Rectangle {
                        visible: layerRow.nodeCount > 1 && (layerRow.prevCount === 1 || layerRow.nextCount === 1)
                        x: layerRow.leftX - root.lineWidth / 2
                        y: root.visualCenterY - root.lineWidth / 2
                        width: layerRow.rightX - layerRow.leftX + root.lineWidth
                        height: root.lineWidth
                        color: Theme.black
                        z: -1
                    }

                    Item {
                        visible: layerRow.hasNextLayer
                        anchors.fill: parent

                        Rectangle {
                            visible: layerRow.nodeCount > 1 && layerRow.nextCount > 1
                            x: layerRow.leftX - root.lineWidth / 2
                            y: root.visualCenterY
                            width: root.lineWidth
                            height: root.iconSize + root.verticalGap
                            color: Theme.black
                            z: -1
                        }

                        Rectangle {
                            visible: layerRow.nodeCount > 1 && layerRow.nextCount > 1
                            x: layerRow.rightX - root.lineWidth / 2
                            y: root.visualCenterY
                            width: root.lineWidth
                            height: root.iconSize + root.verticalGap
                            color: Theme.black
                            z: -1
                        }

                        Rectangle {
                            visible: !(layerRow.nodeCount > 1 && layerRow.nextCount > 1)
                            x: layerRow.centerX - root.lineWidth / 2
                            y: root.visualCenterY
                            width: root.lineWidth
                            height: root.iconSize + root.verticalGap
                            color: Theme.black
                            z: -1
                        }
                    }

                    Repeater {
                        model: layerRow.nodesInLayer

                        delegate: TechTreeNodeView {
                            required property var modelData
                            required property int index

                            x: layerRow.startX + index * (root.iconSize + root.horizontalGap)
                            scale: root.entryScale
                            transformOrigin: Item.TopLeft
                            nodeModel: modelData
                            fillColor: root.nodeFillColor(modelData)

                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.nodeClicked(modelData)
                            }
                        }
                    }
                }
            }

            Item {
                width: 1
                height: root.verticalGap
            }
        }
    }
}