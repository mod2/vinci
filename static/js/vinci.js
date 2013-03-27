$(document).ready(function() {
	// Search box
	// --------------------------------------------------

	$(document).bind('keydown', '/', function() {
		// Focus on the search box
		$("#search input").focus();

		return false;
	});

	$("#search input").bind('keydown', 'esc', function() {
		// Unfocus the search box
		$("#search input").blur();

		return false;
	});

	$("#search input").on('submit', function() {
		var query = $(this).val().trim();

		if (query.length > 1) {
			console.log("Searching for", query);
		} else {
			console.log("Cleared search results");
		}
	});


	// Entry box
	// --------------------------------------------------

	$(document).bind('keydown', 'ctrl+return', function() {
		if ($("#add:focus").length == 0) {
			// Focus the entry box
			$("#add").focus();
		}

		return false;
	});

	$("#add").bind('keydown', 'shift+return', function() {
		var val = $(this).val().trim();
		addEntry(val);

		return false;
	});

	$("#add").bind('keydown', 'ctrl+return', function() {
		// Unfocus the entry box
		$("#add").blur();

		return false;
	});

	$("#add").bind('keydown', 'esc', function() {
		// Unfocus the entry box
		$("#add").blur();

		return false;
	});

	$("form#input").on("submit", function() {
		var val = $(this).find("#add").val().trim();
		addEntry(val);

		return false;
	});
});

function addEntry(text) {
	// Add the entry
	console.log("adding entry:", text);
	$.get(config.url + "add/entry?notebook=" + config.notebook + "&content=" + encodeURIComponent(text), function(data) {
	 	if (data.status == 'success') {
			var entryHTML = '<article class="entry" data-id="' + data.id + '">';
			entryHTML += '<div class="metadata"><a href="' + config.url + config.notebook + '/entry/' + data.url + '">';
			entryHTML += '<date>' + data.date + '</date><time>' + data.time + '</time>';
			entryHTML += '</a></div>';
			entryHTML += '<div class="content">' + data.html + '</div>';
			entryHTML += '</article>';
		
			$(entryHTML).prependTo($("#entries"));	

            // Add yellow highlight
            var entry = $("#entries .entry:first");
            entry.addClass("new");

            // Remove the yellow after two seconds
            setTimeout(function() {
                entry.removeClass("new");
            }, 2000);
		} else {
			alert("Error adding entry");
		}
	});

	// Clear out the entry box
	$("#add").val('');

	// Blur entry box
	$("#add").blur();
}
