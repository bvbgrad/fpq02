/**
 * init.js
 */

"use strict";  // enforce variable declarations – safer coding

// Makes sure the document is ready before executing scripts
function base_js(){

	var utcDate = new Date().toString()
	console.log(utcDate + " base.js was loaded successfully ");

	var footer = document.querySelector('footer');
	footer.setAttribute('class', 'text-muted');
    footer.textContent = 'As of ' + utcDate;

};

$(document).ready(base_js);