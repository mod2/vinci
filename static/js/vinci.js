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
			var q = query.replace(/#(\w+)/g, 'tag:$1');

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


	// Editing entries
	// --------------------------------------------------

	$("#entries").on("click", ".entry .metadata .controls a.edit", function() {
		var entry = $(this).parents(".entry:first");

		if (entry.find(".content:visible").length > 0) {
			// Show the editbox
			$(this).html("Cancel");
			entry.find(".content").fadeOut(75, function() {
				entry.find(".editbox").fadeIn(75, function() {
					$(this).find("textarea").focus();
				});
			});
		} else {
			// Hide the editbox
			$(this).html("Edit");
			entry.find(".editbox").fadeOut(75, function() {
				entry.find(".content").fadeIn(75);
			});
		}

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
                // Update content
                entry.find(".content").html(data.html);

				// Update plugins list
				entry.attr("data-plugins", data.plugins.join(","));

				// For any plugins, call the init function on the newly returned content
				var content = entry.find(".content");
				loadPlugins(content, data.plugins);

                // Update date
                entry.find(".metadata date").html(data.date);
                entry.find(".metadata time").html(data.time);

				// Update tags
				if (data.tags.length > 0) {
					// Add the container if it isn't there
					if (entry.find("ul.tags").length == 0) {
						$("<ul class='tags'></ul>").appendTo(entry);
					} else {
						// Wipe it out
						entry.find("ul.tags").html('');
					}

					var tagHTML = '';
					for (var i in data.tags) {
						var tag = data.tags[i];
						tagHTML += '<li><a href="' + config.url + config.notebook + '/tag/' + tag + '">#' + tag + '</a></li>';
					}

					$(tagHTML).appendTo(entry.find("ul.tags"));
				} else {
					// If there aren't any tags but we still have a container, kill it
					if (entry.find("ul.tags").length > 0) {
						entry.find("ul.tags").remove();
					}
				}

				// Update title
				var title = '';
				if (data.slug) {
					title = (data.title) ? data.title : data.slug;
				}

				if (title != '') {
					if (entry.find(".metadata h2.page-title").length > 0) {
						entry.find(".metadata h2.page-title").html(title);
					} else {
						$('<h2 class="page-title">' + title + '</h2>').appendTo(".metadata");
						entry.find(".metadata a").remove();
					}
				}

                // Add yellow highlight
                entry.addClass("new");

				// Make sure the edit button says "Edit"
				entry.find(".metadata .controls a.edit").html("Edit");

                // Remove the yellow after two seconds
                setTimeout(function() {
                    entry.removeClass("new");
                }, 2000);

                // Hide edit stuff, show content stuff
                entry.find(".editbox").fadeOut(75, function() {
                    entry.find(".content").fadeIn(75);
                });
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

		entry.find(".metadata .controls a.edit").html("Edit");

		// Hide the editbox
		entry.find(".editbox").fadeOut(75, function() {
			entry.find(".content").fadeIn(75);
		});

		return false;
	});

	$(document).bind("keydown", "shift+return", function() {
		console.log("shift+return");
		// Detail, so there's only one entry
		if ($("#entries .entry").length == 1) {
			// Show the editbox
			var entry = $("#entries .entry");

			entry.find(".metadata .controls a.edit").html("Cancel");

			entry.find(".content").fadeOut(75, function() {
				entry.find(".editbox").fadeIn(75, function() {
					$(this).find("textarea").focus();
				});
			});
		}

		return false;
	});

	$("#entries").on("click", ".entry .metadata .controls a.delete", function() {
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
				nbHTML += '<div class="controls"><a href="" class="delete">Delete</a> <a href="" class="edit">Edit</a></div>';
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
			var entryHTML = '<article class="entry" data-id="' + data.id + '" data-plugins="' + data.plugins.join(',') + '">';
			entryHTML += '<div class="metadata">';
			if (data.title == '' && data.slug == '') {
				entryHTML += '<a href="' + config.url + config.notebook + '/entry/' + data.url + '">';
				entryHTML += '<date>' + data.date + '</date><time>' + data.time + '</time>';
				entryHTML += '</a>';
			}
			entryHTML += '<div class="controls"><a href="" class="delete">Delete</a><a href="" class="edit">Edit</a></div>';
			if (data.title != '' || data.slug != '') {
				entryHTML += '<h2 class="page-title">' + ((data.title != '') ? data.title : data.slug) + '</h2>';
			}
			entryHTML += '</div>';
			entryHTML += '<div class="content">' + data.html + '</div>';
			if (data.tags.length > 0) {
				entryHTML += '<ul class="tags">';
				for (var i in data.tags) {
					var tag = data.tags[i];
					entryHTML += '<li><a href="' + config.url + config.notebook + '/tag/' + tag + '">#' + tag + '</a></li>';
				}
				entryHTML += '</ul>';
			}
			entryHTML += '<form class="editbox">';
			entryHTML += '<textarea>' + data.content + '</textarea>';
			entryHTML += '<div class="group"><label>Date:</label><input type="text" value="' + data.datetime + '" /></div>';
			entryHTML += '<input type="submit" value="Save Entry" class="submitbutton" />';
			entryHTML += '</form>';
			entryHTML += '</article>';

			var entry = $(entryHTML).prependTo($("#entries"));	

			// For any plugins, call the init function on the newly returned content
			var content = entry.find(".content");
			loadPlugins(content, data.plugins);

			// Bind shift+return
			entry.find(".editbox textarea, .editbox input[type=text]").bind('keydown', 'shift+return', function() {
				$(this).parents(".editbox").submit();

				return false;
			});

			// Add yellow highlight
			entry.addClass("new");

			// Remove the yellow after two seconds
			setTimeout(function() {
				entry.removeClass("new");
			}, 2000);

			// And update the # entries
			var numEntries = parseInt($("label.num_entries").html().match(/^(\d+)/)[1]);
			$("label.num_entries").html((numEntries + 1) + " entries");

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
