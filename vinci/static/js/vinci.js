// CSRF stuff

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
	// Menu code
	$("a.menu").on("click touchstart", function(e) {
		$("body").toggleClass("active-nav");

		return false;
	});

	$(".mask").on("click touchstart", function(e) {
		$("body").removeClass("active-nav");

		return false;
	});


	// Search
	// --------------------------------------------------

	function _focusSearch() {
		// Display and focus on the search
		$("#search input[type=text]").val('');

		$("#search").slideDown(75, function() {
			$("#search input[type=text]").focus();
		});

		return false;
	}

	function _unfocusSearch() {
		// Unfocus the search box
		$("#search").slideUp(75, function() {
			$("#search input").val('').blur();
		});

		return false;
	}


	// Keyboard shortcuts
	// --------------------------------------------------

	Mousetrap.bind('/', _focusSearch);
	var searchField = document.querySelector('#search input[type=text]');
	Mousetrap(searchField).bind('esc', _unfocusSearch);


	$("#search").on('submit', function() {
		var searchSectionURI = $("#search").attr("data-search-section-uri");

		// Get whatever was entered
		var query = $(this).find("input").val().trim();

		if (query.length > 0) {
			// Search
			var q = query.replace(/#(\w+)/g, 'tag:$1');

			url = searchSectionURI + '?q=' + q;
		} else {
			// Empty search, clear results (don't need to change URL)
		}

		window.location.href = url;

		return false;
	});


	// Infinite scroll
	// --------------------------------------------------

	if ($("nav[role=pagination] a.next")) {
		$(".entries").infinitescroll({
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


	// Editing entries
	// --------------------------------------------------

	function showEditPanel(entry) {
		// Show the edit area
		entry.find(".content, .metadata").fadeOut(100, function() {
			autosize.update(entry.find(".edit-mode textarea"));

			entry.find(".edit-mode").fadeIn(150, function() {
				entry.find(".edit-mode textarea").focus();
			});
		});

		entry.find(".controls-toggle.active").removeClass("active");
	}

	function hideEditPanel(entry) {
		// Blur the textarea
		entry.find(".edit-mode textarea").blur();

		// Hide the edit area
		entry.find(".edit-mode").fadeOut(150, function() {
			entry.find(".content, .metadata").fadeIn(150);
		});

		// Close the advanced panel
		entry.find(".edit-panel .other").hide();

		// Activate the toggle
		entry.find(".controls-toggle.active").removeClass("active");
	}

	// Edit entry toggle

	$(".entries").on("click touchstart", ".entry .controls-toggle", function() {
		var entry = $(this).parents(".entry");

		if (entry.find(".edit-panel:visible").length > 0) {
			hideEditPanel(entry);
		} else {
			showEditPanel(entry);
		}

		return false;
	});

	// Shortcut to edit an entry

	Mousetrap.bind("e", function() {
		if ($(".entry.selected").length > 0) {
			// List page with selected entry
			var entry = $(".list .entry.selected");
			entry.removeClass("selected");
		} else if ($(".entry").length == 1) {
			// Detail
			var entry = $(".entries .entry");
		}

		if (entry) {
			showEditPanel(entry);
		}

		return false;
	});

	// Shortcut to escape out of editing an entry

	var fields = document.querySelectorAll(".edit-mode textarea, .edit-mode input[type=text]");

	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind('esc', function(e) {
			hideEditPanel($(e.target).parents(".entry"));
		});

		Mousetrap(fields[i]).bind('ctrl+t', function(e) {
			toggleOthers($(e.target));
			return false;
		});
	}

	$(".edit-mode .group span.type").on("click", function() {
		var entryType = $(this).attr("data-value");
		var parentEntry = $(this).parents(".entry");

		// Select this one
		$(this).siblings(".selected").removeClass("selected");
		$(this).addClass("selected");

		// Update the hidden field
		parentEntry.find("input[name=type]").val(entryType);

		// Update the parent entry class
		parentEntry.removeClass("log").removeClass("note").removeClass("page").removeClass("journal");
		parentEntry.addClass(entryType);

		return false;
	});

	function toggleOthers(selector) {
		var theOthers = selector.parents(".edit-mode").find(".other");

		if ($(".edit-mode .other:visible").length > 0) {
			theOthers.slideUp(200);
		} else {
			theOthers.slideDown(200);
		}

		return false;
	}

	$(".edit-mode .group.more a").on("click", function() {
		toggleOthers($(this));
	});


	// Autosize
	// --------------------------------------------------

	autosize($("#page #content .entry .edit-mode textarea"));


	// Shortcuts
	// --------------------------------------------------

	Mousetrap.bind('j', function() {
		// If nothing selected, select the first
		if ($(".entries .entry.selected").length == 0) {
			$(".entries .entry:first-child").addClass("selected");
		} else {
			var selected = $(".entries .entry.selected");
			var nextEntry = selected.next();

			if (nextEntry.length > 0) {
				nextEntry.addClass("selected");
				selected.removeClass("selected");

				if (nextEntry.offset().top + nextEntry.height() > $(window).scrollTop() + viewport.height() - 100) {
					$(window).scrollTop($(window).scrollTop() + nextEntry.height() + 100);
				}
			}
		}

		return false;
	});

	Mousetrap.bind('k', function() {
		// If nothing selected, select the first
		if ($(".entries .entry.selected").length == 0) {
			$(".entries .entry:first-child").addClass("selected");
		} else {
			var selected = $(".entries .entry.selected");
			var prevEntry = selected.prev();

			if (prevEntry.length > 0) {
				prevEntry.addClass("selected");
				selected.removeClass("selected");

				if (prevEntry.offset().top < $(window).scrollTop()) {
					$(window).scrollTop($(window).scrollTop() - prevEntry.height() - 80);
				}
			}
		}

		return false;
	});

	// General escape
	Mousetrap.bind('esc', function() {
		// Remove selection
		$(".entries .entry.selected").removeClass("selected");

		// Hide modal if it's there
		if ($("#modal:visible").length) {
			_hideHelp();
		}
	});

	// Go to entry

	Mousetrap.bind('return', function() {
		if ($(".entries .entry.selected").length > 0) {
			var entry = $(".entries .entry.selected");

			window.location.href = entry.attr("data-uri");

			return false;
		}
	});

	// Go to logs section
	Mousetrap.bind('g l', function() {
		var uri = $("#sections").attr("data-log-uri");

		if (uri) {
			window.location.href = uri;
		}

		return false;
	});

	// Go to notes section
	Mousetrap.bind('g n', function() {
		var uri = $("#sections").attr("data-note-uri");

		if (uri) {
			window.location.href = uri;
		}

		return false;
	});

	// Go to pages section
	Mousetrap.bind('g p', function() {
		var uri = $("#sections").attr("data-page-uri");

		if (uri) {
			window.location.href = uri;
		}

		return false;
	});

	// Go to journals section
	Mousetrap.bind('g j', function() {
		var uri = $("#sections").attr("data-journal-uri");

		if (uri) {
			window.location.href = uri;
		}

		return false;
	});

	// All notebooks
	Mousetrap.bind('g h', function() {
		window.location.href = config.url;

		return false;
	});

	// Help dialog
	function _showHelp() {
		$("#mask").fadeIn(200);
		$("#modal").fadeIn(200);
		$("#modal-help").fadeIn(200);
	}

	function _hideHelp() {
		$("#modal-help").fadeOut(200);
		$("#modal").fadeOut(200);
		$("#mask").fadeOut(200);
	}

	Mousetrap.bind('?', _showHelp);
	var modalForm = document.querySelector("#modal");
	Mousetrap(modalForm).bind('esc', _hideHelp);

	// Hide modal on click mask
	$("#mask").on("click", function() {
		_hideHelp();
	});


	// Tags
	$("input[name=tags]").tagit();
});

function processEntries(entries) {
	// Re-run Prism on all entries (old and new)
	// TODO: someday Prism.highlightElement might work, and then we can switch
	// to run it on only new entries, but for now it doesn't work
	Prism.highlightAll();
}
