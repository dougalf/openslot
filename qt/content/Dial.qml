import Qt 4.7

Item {
    id: root
    property real value : 0
	property int minutes
	property int seconds
	property int seconds10

    width: 210; height: 270


	function timeChanged() {
		seconds10 = seconds10 + 1
		if( seconds10 > 99 ) {
			seconds10 = 0
			seconds = seconds + 1
		}
		if( seconds > 59 ) {
			seconds = 0
			minutes = minutes + 1
		}
		if( minutes > 59 ) {
			minutes = 0
		}
		roundspeed.text =  ( minutes < 10 ? "0" : "" ) + minutes + ":" + ( seconds < 10 ? "0" : "" ) + seconds + ":" + ( seconds10 < 10 ? "0" : "" ) + seconds10;
	}

	Timer {
		interval: 100; running: true; repeat: true
		onTriggered: root.timeChanged()
	}

	FontLoader {
		id: segment7
		source: "7segment.ttf"
	}

	Text {
		x: 30
		y: 0
		text: "88:88:88"
		font.pointSize: 40
		color: "grey"
		font.family: segment7.name
	}
	Text {
		id: roundspeed
		x: 30
		y: 0
//		text: root.value
		font.pointSize: 40
		color: "red"
		style: Text.Outline
		font.family: segment7.name
	}

    Image {
		y: 60
		source: "background.png" }

    Image {
        x: 96
        y: 95
        source: "needle_shadow.png"
        transform: Rotation {
            origin.x: 9; origin.y: 67
            angle: needleRotation.angle
        }
    }

    Image {
        id: needle
        x: 98; y: 93
        smooth: true
        source: "needle.png"
        transform: Rotation {
            id: needleRotation
            origin.x: 5; origin.y: 65
            angle: Math.min(Math.max(-130, root.value*2.6 - 130), 133)
            Behavior on angle {
                SpringAnimation {
                    spring: 1.4
                    damping: .15
                }
            }
        }
    }
    Image { x: 21; y: 78; source: "overlay.png" }
}
