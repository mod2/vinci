// grid.js
// by Ben Crowder
 
$(document).ready(function() {
	$(".grid-box").each(function() {
		// Grab the content
		var content = $.trim($(this).html());
		var lines = content.split('\n');
		
		// Parse
		html = '<table>';
		for (var i in lines) {
			var line = $.trim(lines[i]);
			console.log(line);
	
			html += '<tr>';
			for (var x in line) {
				html += '<td';
				if (line[x] == '1') {
					html += ' class="filled"';
				}
				html += '></td>';
			}
			html += '</tr>';
		}
		html += '</table>';

		// replace the div's contents with the generated HTML
		$(this).html(html);
	});
});
