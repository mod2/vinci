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

	$("#search").on('submit', function() {
		var query = $(this).find("input").val().trim();
		var url = config.url;
		if (config.notebook) {
			url += config.notebook + '/';
		}

		if (query.length > 0) {
			var q = query.replace(/#(\w+)/, 'tag:$1');

			url += 'search/' + q;
		} else {
            // Empty search, clear results (don't need to change URL)
        }

		window.location.href = url;

		return false;
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


	// Sorting
	// --------------------------------------------------
	
	$("select#sort").on("change", function() {
		var val = $(this).val();
		var url = window.location.href;

		queryString = window.location.search;

		// If sort is in the query string, replace it
		if (url.match(/sort=/)) {
			newQueryString = queryString.replace(/sort=([^&]+)/, 'sort=' + val);
		} else { // Add it
			// First ignore the ? and split into an array by &
			queryArray = queryString.substr(1).split('&');

			// Add it to the array
			queryArray.push('sort=' + val);

			// And package it back up again
			newQueryString = '?' + queryArray.join('&');
		}

		// Rebuild the URL
		url = window.location.origin + window.location.pathname + newQueryString;

		// Redirect to it
		window.location.href = url;

		return false;
	});
});

function addEntry(text) {
	// Add the entry
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
