import Qt 4.7
import "content"

Rectangle {
    color: "#545454"
    width: 6*210; height: 250

	function updateDial(id, angle) {
		if(id == 1) {
			dial1.value = angle
		}
		if(id == 2) {
			dial2.value = angle
		}
		if(id == 3) {
			dial3.value = angle
		}
		if(id == 4) {
			dial4.value = angle
		}
		if(id == 5) {
			dial5.value = angle
		}
		if(id == 6) {
			dial6.value = angle
		}
	}

	Row {
		Dial {
			id: dial1
			value: 0
		}
		Dial {
			id: dial2
			value: 0
		}
		Dial {
			id: dial3
			value: 0
		}
		Dial {
			id: dial4
			value: 0
		}
		Dial {
			id: dial5
			value: 0
		}
		Dial {
			id: dial6
			value: 0
		}
    }
}
