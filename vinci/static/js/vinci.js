function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(document).ready(function() {
	// Infinite scroll
	if ($("nav[role=navigation] a.next")) {
		$("#entries").infinitescroll({
			navSelector: "nav[role=pagination]",
			nextSelector: "nav[role=pagination] a.next",
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
		if ($("#cmdline:visible").length == 0) {
			$("#cmdline input").val('');
			$("#cmdline").slideDown(50);
			$("#cmdline input").focus();
		} else {
			$("#cmdline input").blur();
			$("#cmdline").slideUp(50);
		}

		return false;
	});

	$(document).bind('keydown', '/', function() {
		// Focus on the command line
		$("#cmdline input").val('');
		$("#cmdline").slideDown(50);
		$("#cmdline input").focus();

		return false;
	});

	$("#cmdline input").bind('keydown', 'esc', function() {
		// Unfocus the search box
		$("#cmdline input").blur();
		$("#cmdline").slideUp(50);

		return false;
	});

	$("#cmdline").on('submit', function() {
		var url = config.url;
		if (config.notebook) {
			url += config.notebook + '/';
		}

		// Get whatever was entered
		var query = $(this).find("input").val().trim();

		if (query.length > 0) {
			// See if it was a search or a command (commands start with ':')
			if (query[0] == ':') {
				// Command
				var commandString = query.slice(1);
				var command = commandString.split(' ')[0];
				var args = commandString.split(' ').slice(1);

				// Convert args back to a string (do we really need to do this?)
				if (args.length > 0) {
					args = args.join(' ');
				}

				// Todo: make this better
				if (command == 'g' || command == ':') {
					// Go (g / :)

					// If there's not a slash, it's a notebook name
					// If there's a slash, it's notebook/entry

					if (args.indexOf('/') != -1) {
						// Notebook/entry
						var argsArray = args.split('/');
						url = config.url + argsArray[0] + '/entry/' + argsArray[1];
					} else {
						// Just a notebook name
						url = config.url + args;
					}

					window.location.href = url;
				} else if (command == 'ge') {
					// Go to entry in current notebook (ge)

					url += 'entry/' + args;

					window.location.href = url;
				} else if (command == 'x') {
					// Execute Javascript

					// Only do this on a detail page
					if ($("#entries").hasClass("detail")) {
						// Prep input
						input = $(".editbox textarea").text();

						try {
							// Execute the command (which gets assigned to the output var)
							eval("output = " + args);

							// And update the textarea
							$(".editbox textarea").text(output);

							// Show the edit box so we can save it if we want
							var entry = $("article.entry");
							entry.find(".content").fadeOut(75, function() {
								entry.find(".editbox").fadeIn(75, function() {
									$(this).find("textarea").focus();
								});
							});
						} catch (e) {
							console.log("Failed to execute the command");
						}
					}
				} else if (command == 'diary') {
					// Go to diary mode
					window.location.pathname = '/diary/' + args;
				}

				return false;
			} else {
				// Search
				var q = query.replace(/#(\w+)/g, 'tag:$1');

				url += 'search/' + q;
			}
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
	//
	$("body > header nav ul li a.addentry").on("click touchstart", function() {
		if ($("#input:visible").length == 0) {
			// Show the entry area
			$("#input").slideDown(50);

			// Focus the entry box
			$("#add").focus();
		} else {
			// Unfocus the entry box
			$("#input").slideUp(50);
		}

		return false;
	});

	$(document).bind('keydown', 'ctrl+return', function() {
		if ($("#add:focus").length == 0) {
			// Show the entry area
			$("#input").slideDown(50);

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
		$("#input").slideUp(50);

		return false;
	});

	$("#add").bind('keydown', 'esc', function() {
		// Unfocus the entry box
		$("#add").blur();
		$("#input").slideUp(50);

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

	$("#entries").on("click touchstart", ".entry .menu a", function() {
		$(this).parents(".entry").siblings(".entry").find(".more").hide();
		$(this).parents(".menu").siblings(".more").toggle();

		return false;
	});

	$("body").on("click", function() {
		if ($(".more").length > 0) {
			$(".more").hide();
		}
	});


	// Editing entries
	// --------------------------------------------------

	$("#entries").on("click touchstart", ".entry .metadata a.edit", function() {
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
		var title = entry.find(".editbox input[name=title]").val().trim();
		var tags = entry.find(".editbox input[name=tags]").val().trim();

		var date = '';
		if (entry.find(".editbox input[type=text]").length > 0) {
			date = entry.find(".editbox input[type=text]").val().trim();
		}

		// Call edit entry web service
        var url = config.url + "api/" + config.notebook + "/" + id + "/";

        data = {
			content: text,
		};

		if (date) {
            data['date'] = date;
		}

		if (title) {
			data['title'] = title;
		}

		if (tags) {
			data['tags'] = tags;
		}

        $.ajax({
            method: "PUT",
            url: url,
            data: data,
            success: function(data) {
                // Reload the page
                location.reload(false);
            },
            error: function(data) {
                alert("Error editing entry");
            },
        });

        return false;
	});

	$(document).on("keydown", "textarea#add, .editbox textarea", function(e) {
		if (e.keyCode === 9) {
			var start = this.selectionStart;
			var end = this.selectionEnd;

			var $this = $(this);
			var value = $this.val();

			$this.val(value.substring(0, start) + "\t" + value.substring(end));

			this.selectionStart = this.selectionEnd = start + 1;
			e.preventDefault();
		}
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
			var url = config.url + "api/" + config.notebook + "/" + id + "/";

			$.ajax({
				method: "DELETE",
				url: url,
				success: function(data) {
					// Fade out and then delete the DOM element
					entry.fadeOut(75, function() {
						entry.remove();
					});
					// Redirect to notebook page
					window.location.href = config.url + config.notebook;
				},
				error: function(data) {
					alert("Error deleting entry");
				},
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
		var url = config.url + "api/";

		// Add the notebook
		$.post(url, {name: name}, function(data) {
            var nbHTML = '<article class="notebook" data-slug="' + data.slug + '">';
            nbHTML += '<div class="controls"><a href="" class="delete">delete</a> <a href="" class="edit">edit</a></div>';
            nbHTML += '<a href="' + config.url + data.slug + '">';
            nbHTML += '<h2>' + data.name + '</h2>';
            nbHTML += '</a>';
            nbHTML += '<form class="editbox nb-edit-box">';
            nbHTML += '<div class="group"><label>Name:</label> <input type="text" class="name" value="' + data.name + '" /></div>';
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
            });
		}, 'json');

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

		// Call edit notebook web service
        var url = config.url + "api/" + slug + '/';

        $.ajax({
            method: 'PUT',
            url: url,
            data: {name: name},
            success: function(data) {
                // Update content
                nb.find("> a h2").html(data.name);
				nb.attr("data-slug", data.slug);

                // Hide edit stuff
                nb.find(".editbox").fadeOut(75);
            },
            error: function(data) {
                alert("Error editing notebook");
            },
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
			var url = config.url + "api/" + slug + '/';

			$.ajax({
				method: "DELETE",
				url: url,
				success: function(data) {
					// Fade out and then delete the DOM element
					nb.fadeOut(75, function() {
						nb.remove();
					});
				},
				error: function(data) {
					alert("Error deleting notbook");
				}
			});
		}

		return false;
	});
});

function addEntry(text) {
	// Add the entry
	// TODO: doesn't work, might need to send the csrf token or something
	$.ajax({
		method: "POST",
		url: config.url + "api/" + config.notebook + "/",
		data: {content: text},
		success: function(data) {
			// Reload notebook page
			window.location.href = config.url + config.notebook + "/";
		},
		error: function(data) {
			alert("Error adding entry");
		},
	});

	// Clear out the entry box
	$("#add").val('');

	// Blur entry box
	$("#add").blur();
	$("#add").removeClass('has-text');

	// Hide input area
	$("#input").slideUp(50);
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
