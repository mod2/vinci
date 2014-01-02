$(document).ready(function() {
	// Infinite scroll
	if ($("nav[role=navigation] a.next")) {
		$("#entries").infinitescroll({
			navSelector: "nav[role=pagination] .links",
			nextSelector: "nav[role=pagination] .links a.next",
			itemSelector: "article.entry",
			loading: {
				finishedMsg: '<i>The very end.</i>',
			},
		}, processEntries);
	}


	// Add viewport to the window object
	// http://geekswithblogs.net/khillinger/archive/2009/06/04/jquery-and-the-viewport-dimensions.aspx
	// --------------------------------------------------

	window.viewport = {
		height: function() { return $(window).height(); },
		width: function() { return $(window).width(); },
		scrollTop: function() { return $(window).scrollTop(); },
		scrollLeft: function() { return $(window).scrollLeft(); }
	};


	// Search box
	// --------------------------------------------------

	$("body > header nav ul li a.search").on("click touchstart", function() {
		$("#search").toggle();

		return false;
	});

	$(document).bind('keydown', '/', function() {
		// Focus on the search box
		$("#search").show();
		$("#search input").focus();

		return false;
	});

	$("#search input").bind('keydown', 'esc', function() {
		// Unfocus the search box
		$("#search input").blur();
		$("#search").hide();

		return false;
	});

	$("#search").on('submit', function() {
		var query = $(this).find("input").val().trim();
		var url = config.url;
		if (config.notebook) {
			url += config.notebook + '/';
		}

		if (query.length > 0) {
			var q = query.replace(/#(\w+)/g, 'tag:$1');

			url += 'search/' + q;
		} else {
			// Empty search, clear results (don't need to change URL)
		}

		window.location.href = url;

		return false;
	});


	// Entry list
	// --------------------------------------------------

	$(document).bind('keydown', 'j', function() {
		// If nothing selected, select the first
		if ($(".list .entry.selected").length == 0) {
			$(".list .entry:first-child").addClass("selected");
		} else {
			var selected = $(".list .entry.selected");
			var nextEntry = selected.next();

			if (nextEntry.length > 0) {
				nextEntry.addClass("selected");
				selected.removeClass("selected");

				if (nextEntry.offset().top + nextEntry.height() > $(window).scrollTop() + viewport.height() - 100) {
					$(window).scrollTop($(window).scrollTop() + nextEntry.height() + 100);
				}
			}
		}

		// TODO: pagination

		return false;
	});

	$(document).bind('keydown', 'k', function() {
		// If nothing selected, select the first
		if ($(".list .entry.selected").length == 0) {
			$(".list .entry:first-child").addClass("selected");
		} else {
			var selected = $(".list .entry.selected");
			var prevEntry = selected.prev();

			if (prevEntry.length > 0) {
				prevEntry.addClass("selected");
				selected.removeClass("selected");

				if (prevEntry.offset().top < $(window).scrollTop()) {
					$(window).scrollTop($(window).scrollTop() - prevEntry.height() - 80);
				}
			}
		}

		// TODO: pagination

		return false;
	});


	$(document).bind('keydown', 'return', function() {
		if ($(".list .entry.selected").length > 0) {
			// Go to the selected entry

			if ($(".list .entry.selected .metadata > a").length > 0) {
				// Entry
				window.location.href = $(".list .entry.selected .metadata > a").attr('href');
			} else if ($(".list .entry.selected h3 a").length > 0) {
				// Page
				window.location.href = $(".list .entry.selected h3 a").attr('href');
			}

			return false;
		}
	});


	// Shortcuts
	// --------------------------------------------------

	// Notebook page
	$(document).bind('keydown', 'n', function() {
		if (config.notebook) {
			window.location.href = config.url + config.notebook;
		}

		return false;
	});

	// Notebook/entry/home
	$(document).bind('keydown', 'h', function() {
		if (config.notebook) {
			window.location.href = config.url + config.notebook + '/entry/home';
		}

		return false;
	});

	// All notebooks
	$(document).bind('keydown', 'a', function() {
		window.location.href = config.url;

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
		$(this).removeClass('has-text');

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

	$("#add").on('change', function() {
		if ($(this).val().trim().length > 0 && !$(this).hasClass('has-text')) {
			$(this).addClass('has-text');
		} else if ($(this).val().trim().length == 0) {
			$(this).removeClass('has-text');
		}
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


	// Action bar
	// --------------------------------------------------
	
	$("#entries").on("click tap", ".entry .menu a", function() {
		$(this).parents(".menu").siblings(".more").toggle();

		return false;
	});



	// Editing entries
	// --------------------------------------------------

	$("#entries").on("click", ".entry .metadata a.edit", function() {
		var entry = $(this).parents(".entry:first");

		if (entry.find(".content:visible").length > 0) {
			// Show the editbox
			entry.find(".content").fadeOut(75, function() {
				entry.find(".editbox").fadeIn(75, function() {
					$(this).find("textarea").focus();
				});
			});

			// Change text
			entry.find(".metadata a.edit").html("Cancel");
		} else {
			// Hide the editbox
			entry.find(".editbox").fadeOut(75, function() {
				entry.find(".content").fadeIn(75);
			});

			// Change text
			entry.find(".metadata a.edit").html("Edit");
		}

		// Hide the menu
		entry.find(".metadata .more").hide();

		return false;
	});

	$("#entries").on("submit", ".entry .editbox", function() {
		var entry = $(this).parents(".entry:first");
        var id = entry.attr("data-id");
		var text = entry.find(".editbox textarea").val().trim();
		var date = '';
		if (entry.find(".editbox input[type=text]").length > 0) {
			date = encodeURIComponent(entry.find(".editbox input[type=text]").val().trim());
		}

		// Call edit entry web service
        var url = config.url + "edit/entry/?id=" + id + "&notebook=" + config.notebook;
		if (date) {
			url += "&date=" + date;
		}

        $.post(url, { content: text }, function(data) {
            if (data.status == 'success') {
				// Reload the page
				location.reload(false);
            } else {
                alert("Error editing entry");
            }
        });

        return false;
	});

	$("#entries").on("keydown", ".entry .editbox textarea, .entry .editbox input[type=text]", "shift+return", function() {
		$(this).parents(".editbox").submit();

		return false;
	});

	$("#entries").on("keydown", ".entry .editbox textarea, .entry .editbox input[type=text]", "esc", function() {
		var entry = $(this).parents(".entry:first");

		// Hide the editbox
		entry.find(".editbox").fadeOut(75, function() {
			entry.find(".content").fadeIn(75);
		});

		// Change text
		entry.find(".metadata a.edit").html("Edit");

		// Hide the menu
		entry.find(".metadata .more").hide();

		return false;
	});

	$(document).bind("keydown", "shift+return", function() {
		if ($("#entries .entry").length == 1) {
			// Detail, so there's only one entry
			var entry = $("#entries .entry");
		} else {
			// List page, see if we have a selected entry
			var entry = $(".list .entry.selected");
		}

		if (entry) {
			// Show the editbox
			entry.find(".content").fadeOut(75, function() {
				entry.find(".editbox").fadeIn(75, function() {
					$(this).find("textarea").focus();
				});
			});

			// Change text
			entry.find(".metadata a.edit").html("Cancel");

			// Hide the menu
			entry.find(".metadata .more").hide();
		}

		return false;
	});

	$("#entries").on("click", ".entry .metadata a.delete", function() {
		if (confirm("Do you really want to delete that entry?")) {
			var entry = $(this).parents(".entry:first");
			var id = entry.attr("data-id");

			// Call delete entry web service
			var url = config.url + "delete/entry?id=" + id + "&notebook=" + config.notebook;

			$.get(url, function(data) {
				if (data.status == 'success') {
					// Fade out and then delete the DOM element
					entry.fadeOut(75, function() {
						entry.remove();
					});
				} else {
					alert("Error deleting entry");
				}
			});
		}

		return false;
	});


	// Adding a notebook
	// --------------------------------------------------

	$("a.addnotebook").on("click", function() {
		// Toggle the view
		if ($(".addbox:visible").length > 0) {
			// Hide the addbox 
			$(".addbox").fadeOut(75);
		} else {
			// Show the addbox
			$(".addbox").fadeIn(75, function() {
				$(".addbox input[type=text]").focus();
			});
		}

		return false;
	});

	$(".addbox textarea, .addbox input[type=text]").bind('keydown', 'shift+return', function() {
		$(this).parents(".addbox").submit();

		return false;
	});

	$(".addbox").on("submit", function() {
		var name = encodeURIComponent($(this).find(".name").val().trim());
		var desc = encodeURIComponent($(this).find(".desc").val().trim());
		var url = config.url + "add/notebook?name=" + name + "&description=" + desc;

		console.log(url);

		// Add the notebook
		$.get(url, function(data) {
			if (data.status == 'success') {
				var nbHTML = '<article class="notebook" data-slug="' + data.slug + '">';
				nbHTML += '<div class="menu"><a href="" class="delete">Delete</a> <a href="" class="edit">Edit</a></div>';
				nbHTML += '<a href="' + config.url + data.slug + '">';
				nbHTML += '<h2>' + data.name + '</h2>';
				if (data.description) {
					nbHTML += '<p>' + data.description + '</p>';
				}
				nbHTML += '</a>';
				nbHTML += '<form class="editbox nb-edit-box">';
				nbHTML += '<div class="group"><label>Name:</label> <input type="text" class="name" value="' + data.name + '" /></div>';
				nbHTML += '<label>Description:</label><textarea class="desc">';
				if (data.description) nbHTML += data.description;
				nbHTML += '</textarea>';
				nbHTML += '<input type="submit" value="Save Notebook" class="submitbutton" />';
				nbHTML += '</form>';
				nbHTML += '</article>';
			
				var nb = $(nbHTML).appendTo($("#notebooks"));
				
				nb.find(".editbox textarea, .editbox input[type=text]").bind('keydown', 'shift+return', function() {
					$(this).parents(".editbox").submit();

					return false;
				});

				$(".addbox").fadeOut(75, function() {
					$(this).find(".name").val('');
					$(this).find(".desc").val('');
				});
			} else {
				alert("Error adding notebook");
			}
		});

		return false;
	});


	// Editing notebooks
	// --------------------------------------------------

	$("#notebooks").on("click", ".notebook .controls a.edit", function() {
		var nb = $(this).parents(".notebook:first");

		if (nb.find(".editbox:visible").length == 0) {
			// Show the editbox
			nb.find(".editbox").fadeIn(75, function() {
				$(this).find(".name").focus()
			});
		} else {
			// Hide the editbox
			nb.find(".editbox").fadeOut(75);
		}

		return false;
	});

	$("#notebooks").on("submit", ".notebook .editbox", function() {
		var nb = $(this).parents(".notebook:first");
        var slug = nb.attr("data-slug");
        var name = encodeURIComponent(nb.find(".editbox input[type=text]").val().trim());
		var desc = encodeURIComponent(nb.find(".editbox textarea").val().trim());

		// Call edit notebook web service
        var url = config.url + "edit/notebook?notebook=" + slug + "&name=" + name + "&description=" + desc;

        $.get(url, function(data) {
            if (data.status == 'success') {
                // Update content
                nb.find("> a h2").html(data.name);
                nb.find("> a p").html(data.description);
				nb.attr("data-slug", data.slug);

                // Hide edit stuff
                nb.find(".editbox").fadeOut(75);
            } else {
                alert("Error editing notebook");
            }
        });

        return false;
	});

	$(".notebook .editbox textarea, .notebook .editbox input[type=text]").bind('keydown', 'shift+return', function() {
		$(this).parents(".editbox").submit();

		return false;
	});

	$("#notebooks").on("click", ".notebook .controls a.delete", function() {
		if (confirm("Do you really want to delete that notebook?")) {
			var nb = $(this).parents(".notebook:first");
			var slug = nb.attr("data-slug");

			// Call delete notebook web service
			var url = config.url + "delete/notebook?notebook=" + slug;

			$.get(url, function(data) {
				if (data.status == 'success') {
					// Fade out and then delete the DOM element
					nb.fadeOut(75, function() {
						nb.remove();
					});
				} else {
					alert("Error deleting notebook");
				}
			});
		}

		return false;
	});
});

function addEntry(text) {
	// Add the entry
	$.post(config.url + "add/entry/?notebook=" + config.notebook, { content: text }, function(data) {
	 	if (data.status == 'success') {
			// Reload the page
			location.reload(false);
		} else {
			alert("Error adding entry");
		}
	});

	// Clear out the entry box
	$("#add").val('');

	// Blur entry box
	$("#add").blur();
	$("#add").removeClass('has-text');
}

function loadPlugins(content, plugins) {
	for (var i=0; i<plugins.length; i++) {
		var plugin = plugins[i];

		var plugin_function = plugin + "_init";

		if (plugin_function in window) {
			window[plugin_function](content);
		}
	}
}

function processEntries(entries) {
	for (i in entries) {
		var entry = $(entries[i]);

		if ($(entry).attr("data-plugins")) {
			var plugins = entry.attr("data-plugins").split(',');

			entry.find(".content").each(function() {
				loadPlugins($(this), plugins);
			});
		}
	}
}
