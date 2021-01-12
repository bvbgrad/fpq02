/**
 * init.js
 */

"use strict";  // enforce variable declarations – safer coding

// Makes sure the document is ready before executing scripts
function base_js(){

	var utcDate = new Date().toString()
	console.log(utcDate + " base.js was loaded successfully ");

	var footerStatus = document.querySelector('#footerStatus');
	footerStatus.setAttribute('class', 'text-muted');
    footerStatus.textContent = utcDate;

};

$(document).ready(base_js);