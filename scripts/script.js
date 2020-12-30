// RGB Slider Compiler
function compileColor() {
	// Parse RGB as Hex
	var rgbToHex = function (rgb) { 
		var hex = Number(rgb).toString(16);
		if (hex.length < 2) {hex = "0" + hex}
		return hex;
	};
	var colorHex = rgbToHex(slider[0].value) + rgbToHex(slider[1].value) + rgbToHex(slider[2].value);
	return colorHex;
}

// Set Position of RGB Sliders
function setSliders(hexCode) {
	slider[0].value = parseInt(hexCode.slice(0,2),16)
	slider[0].nextSibling.innerHTML = parseInt(hexCode.slice(0,2),16)
	slider[1].value = parseInt(hexCode.slice(2,4),16)
	slider[1].nextSibling.innerHTML = parseInt(hexCode.slice(2,4),16)
	slider[2].value = parseInt(hexCode.slice(4,6),16)
	slider[2].nextSibling.innerHTML = parseInt(hexCode.slice(4,6),16)
}

// Change visibilities for autotake
function autotake() {
    if (document.getElementById('autotake').checked == true) {
        // Grey out Take Button
        document.getElementById('take').style.opacity = "0.3";
        // Uncheck Auto-dissolve
        document.getElementById('autodissolve').checked = false;
        document.getElementById('autowipe').checked = false;
        // Call autodissolve to perform unchecked actions
        autodissolve();
        autowipe();
    } else {
        // Restore color to take button
        document.getElementById('take').style.opacity = "1";
    }
}

// Change visibilities for auto-dissolve
function autodissolve() {
    if (document.getElementById('autodissolve').checked == true) {
        // Grey out dissolve Button
        document.getElementById('dissolve').style.opacity = ".3";
        // Uncheck auto-take
        document.getElementById('autotake').checked = false;
        document.getElementById('autowipe').checked = false;
        // Call autotake to perform unchecked actions
        autotake();
        autowipe();
    } else {
        // Restore color to dissolve button
        document.getElementById('dissolve').style.opacity = "1";
    }
}

// Change visibilities for auto-wipe
function autowipe() {
    if (document.getElementById('autowipe').checked == true) {
        // Grey out Button
        document.getElementById('wipe').style.opacity = "0.3";
        // Uncheck auto-take
        document.getElementById('autotake').checked = false;
        // Uncheck Auto-dissolve
        document.getElementById('autodissolve').checked = false;
        // perform unchecked actions
        autotake();
        autodissolve();
    } else {
        // Restore color to button
        document.getElementById('wipe').style.opacity = "1";
    }
}

window.addEventListener("load", function() {
	// Global Vars for Sliders
    slider = document.getElementsByClassName("slider");
    // Initiate Dissolve Timer
    DissolveTimer=0;
	
	// Create stylesheet for palSwitch
	style = document.createElement('style');
	document.head.appendChild(style);
	style.sheet.insertRule('hr {margin-left:0;',0);
	
	// Add Palswitch Event Handler
	var items = document.getElementById('palSwitch').getElementsByTagName('li');
	for (var i = 0; i < items.length; i++) {items[i].onclick = palSwitch}
	
	function palSwitch(ev) {
		if (ev.currentTarget.innerHTML == "RGB") {
			document.getElementById('slidecontainer').style.display = "inline-block"
			document.getElementById('buttonContainer').style.display = "none"
			document.getElementById('settings').style.display = "none"
			style.sheet.deleteRule(0);
			style.sheet.insertRule('hr {margin-left:0%;',0);
		} else if (ev.currentTarget.innerHTML == "Palette") {
			document.getElementById('slidecontainer').style.display = "none"
			document.getElementById('buttonContainer').style.display = "inline-block"
			document.getElementById('settings').style.display = "none"
			style.sheet.deleteRule(0);
			style.sheet.insertRule('hr {margin-left:33%;',0);
		} else if (ev.currentTarget.innerHTML == "Settings")  {
			document.getElementById('settings').style.display = "inline-block"
			document.getElementById('slidecontainer').style.display = "none"
			document.getElementById('buttonContainer').style.display = "none"
			style.sheet.deleteRule(0);
			style.sheet.insertRule('hr {margin-left:66%;width:33%;',0);
		} else { // RGB + Palette
			document.getElementById('settings').style.display = "none"
			document.getElementById('slidecontainer').style.display = "inline-block"
			document.getElementById('buttonContainer').style.display = "inline-block"
			style.sheet.deleteRule(0);
			style.sheet.insertRule('hr {margin-left:0%;width:66%;',0);
		}
	}
});
