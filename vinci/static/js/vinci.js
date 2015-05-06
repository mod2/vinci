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

	$(document).bind('keydown', '/', function() {
		// Focus on the search
		$("#search input[type=text]").val('').focus();

		return false;
	});

	$("#search input[type=text]").bind('keydown', 'esc', function() {
		// Unfocus the search box
		$("#search input").val('').blur();

		return false;
	});

	$("#search").on('submit', function() {
		var url = config.url;
		if (config.notebook) {
			url += config.notebook + '/';
		}

		// Get whatever was entered
		var query = $(this).find("input").val().trim();

		if (query.length > 0) {
			// Search
			var q = query.replace(/#(\w+)/g, 'tag:$1');

			url += 'search/?q=' + q;
		} else {
			// Empty search, clear results (don't need to change URL)
		}

		window.location.href = url;

		return false;
	});


	// Infinite scroll
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


	// Entry edit controls
	// --------------------------------------------------

	$(".entries").on("click touchstart", ".entry .controls-toggle", function() {
		if ($(this).siblings(".controls:visible").length) {
			$(this).siblings(".controls").slideUp(150);
			$(this).removeClass("active");
		} else {
			$(this).siblings(".controls").slideDown(150);
			$(this).addClass("active");
		}

		return false;
	});

	$("body").on("click touchstart", function() {
		if ($(".controls:visible").length > 0) {
			$(".controls").slideUp(150);
			$(".controls-toggle.active").removeClass("active");
		}
	});


	// Editing entries
	// --------------------------------------------------

	$(".entries").on("click touchstart", ".entry .controls a.edit", function() {
		var entry = $(this).parents(".entry");

		if (entry.find(".content:visible").length > 0) {
			// Show the edit area
			entry.find(".edit-mode").slideDown(150, function() {
				entry.find(".content, .metadata").slideUp(150, function() {
					$(this).find("textarea").focus();
				});
			});

			// Change text
			entry.find(".controls a.edit").html("Cancel");

			// Hide the menu
			$(".controls").slideUp(150);
			$(".controls-toggle.active").removeClass("active");
		} else {
			// Hide the edit area
			entry.find(".content, .metadata").slideDown(150, function() {
				entry.find(".edit-mode").slideUp(150);
			});

			// Change text
			entry.find(".controls a.edit").html("Edit");

			// Hide the menu
			$(".controls").slideUp(150);
			$(".controls-toggle.active").removeClass("active");
		}

		return false;
	});


	// Autosize
	// --------------------------------------------------

	$("#page #content .entry .edit-mode textarea").autosize();


	// Shortcuts
	// --------------------------------------------------

	$(document).bind('keydown', 'j', function() {
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

	$(document).bind('keydown', 'k', function() {
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

	$(document).bind('keydown', 'return', function() {
		if ($(".entries .entry.selected").length > 0) {
			var entry = $(".entries .entry.selected");

			window.location.href = entry.attr("data-uri");

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

});

function processEntries(entries) {
	// Re-run Prism on all entries (old and new)
	// TODO: someday Prism.highlightElement might work, and then we can switch
	// to run it on only new entries, but for now it doesn't work
	Prism.highlightAll();
}
