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
	function _toggleMenu() {
		$("body").toggleClass("active-nav");
	}

	function _showMenu() {
		$("body").addClass("active-nav");
	}

	function _hideMenu() {
		$("body").removeClass("active-nav");
	}

	$("a.menu").on("click touchstart", function() {
		_toggleMenu();
		return false;
	});

	$(".mask").on("click touchstart", function(e) {
		_hideMenu();
		return false;
	});


	// Error
	// --------------------------------------------------
	
	function _showError(label, message) {
		var html = "<h2>" + label + "</h2>";
		if (message != '') {
			html += "<span class='sub'>" + message + "</span>";
		}

		$("#error .container").html(html);
		$("#error").slideDown(75);
	}


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
			$("#search").removeClass("quickjump");
			$("#search .results").html('').hide();
		});

		return false;
	}


	// Quickjump
	// --------------------------------------------------

	function _focusQuickJump() {
		// Display and focus on the search with quickjump enabled
		$("#search input[type=text]").val('');
		$("#search .results").html('').hide();
		$("#search").addClass("quickjump");

		$("#search").slideDown(75, function() {
			$("#search input[type=text]").focus();
		});

		return false;
	}


	// Keyboard shortcuts
	// --------------------------------------------------

	Mousetrap.bind('g m', _toggleMenu);

	Mousetrap.bind('/', _focusSearch);
	Mousetrap.bind('g /', _focusQuickJump);

	var field = document.querySelector('#search input[type=text]');
	Mousetrap(field).bind('esc', _unfocusSearch);
	// _unfocusSearch also handles clearing out the quickjump

	$("#search").on('submit', _executeSearch);

	function _executeSearch() {
		var url = '';

		var quickJump = $("#search").hasClass("quickjump");

		if (quickJump && $("#search .results a").length > 0) {
			// Go to the first one
			var result = $("#search .results a:first-child");
			var url = result.attr("href");
		} else if ($("#search").hasClass("all") && $(".notebooks .notebook:visible").length == 1) {
			// If we're on the all notebooks page and there's only one notebook selected, choose it
			var notebook = $(".notebooks .notebook:visible");
			var url = notebook.attr("data-uri");
		} else {
			var searchSectionURI = $("#search").attr("data-search-section-uri");
			var query = $("#search input[type=text]").val().trim();

			if (query.length > 0) {
				// Search
				var q = query.replace(/#(\w+)/g, 'tag:$1');

				var url = searchSectionURI + '?q=' + q;
			}
		}

		if (url) {
			window.location.href = url;
		}

		return false;
	}

	// Quickjump
	$("#page").on("input", "#search.quickjump", function() {
		// On typing, call the API
		var url = $("#search.quickjump").attr("data-quickjump-uri");
		var query = $("#search.quickjump input[type=text]").val().trim();

		if (query) {
			$.ajax({
				url: url + "?q=" + query,
				method: 'GET',
				contentType: 'application/json',
				success: function(data) {
					var html = '';

					for (var i in data.results.notebooks) {
						var nb = data.results.notebooks[i];

						html += '<a class="notebook" href="' + nb.url + '" data-slug="' + nb.slug + '">' + nb.name + '</a>';
					}

					for (var i in data.results.pages) {
						var p = data.results.pages[i];

						html += '<a class="page" href="' + p.url + '" data-slug="' + p.slug + '">' + p.name + ' <span class="sub">(' + p.notebook + ')</span></a>';
					}

					for (var i in data.results.tags) {
						var t = data.results.tags[i];

						html += '<a class="tag" href="' + t.url + '" data-slug="' + t.slug + '">#' + t.name + '</a>';
					}

					if (html) {
						$("#search .results").html(html).show();
					} else {
						$("#search .results").html(html).hide();
					}
				},
				error: function(data) {
					_showError("Error getting quickjump results", data);
				},
			});
		} else {
			// Hide quickjump results
			$("#search .results").html('').hide();
		}
	});

	function _followQuickJump() {
		if ($("#search .results a").length > 0) {
			// Go to the first one
			var result = $("#search .results a:first-child").attr("href");

			window.location.href = result;
		}

		return false;
	}


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
		// Hide any other edit panels
		$(".entries .edit-mode:visible").fadeOut(150, function() {
			$(this).find(".edit-panel .other").hide();
			$(this).siblings(".content, .metadata").fadeIn(150);
		});

		// Show the edit area
		entry.find(".content, .metadata").fadeOut(100, function() {
			autosize.update(entry.find(".edit-mode textarea"));

			entry.find(".edit-mode").fadeIn(150, function() {
				entry.find(".edit-mode textarea").focus();
			});
		});

		entry.find(".controls-toggle.active").removeClass("active");

		return false;
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

		return false;
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

	// Shortcut to edit an entry or a notebook

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

		if ($(".notebook.selected").length > 0) {
			// List page with selected entry
			var notebook = $(".notebooks .notebook.selected");
			notebook.removeClass("selected");
			showNotebookEditPanel(notebook);
		}

		return false;
	});

	// Shortcut to escape out of editing an entry

	var fields = document.querySelectorAll(".edit-mode");

	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind('esc', function(e) {
			hideEditPanel($(e.target).parents(".entry"));
			hideNotebookEditPanel($(e.target).parents(".notebook"));
		});

		Mousetrap(fields[i]).bind('ctrl+t', function(e) {
			toggleOthers($(e.target));
			return false;
		});
	}

	// Cmd+Enter (or Ctrl+Enter) to save and close an entry
	var fields = document.querySelectorAll(".edit-mode textarea");
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind('mod+enter', function(e) {
			autoSave(function() {
				hideEditPanel($(e.target).parents(".entry"));
			});
		});
	}

	$(".edit-mode .group span.type").on("click", function() {
		var entryType = $(this).attr("data-value");
		if ($(this).parents("#add-entry").length > 0) {
			console.log("add entry");
			var parentEntry = $("#add-entry");
		} else {
			console.log("not entry");
			var parentEntry = $(this).parents(".entry");
		}

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

		return false;
	});


	// Autosize
	// --------------------------------------------------

	autosize($("#page #content .entry .edit-mode textarea"));


	// Shortcuts
	// --------------------------------------------------

	Mousetrap.bind('j', function() {
		if ($(".list .entries").length) {
			var selector = ".list .entries .entry";
			var type = "entry";
		} else if ($(".all .notebooks").length) {
			var selector = ".all .notebooks .notebook";
			var type = "notebook";
		} else {
			return;
		}

		// If nothing selected, select the first
		if ($(selector + ".selected").length == 0) {
			if (type == "entry") {
				$(selector + ":first-child").addClass("selected");
			} else if (type == "notebook") {
				$(".all .notebooks:first-child .notebook:first-child").addClass("selected");
			}
		} else {
			var selected = $(selector + ".selected");
			var nextItem = selected.next();

			if (nextItem.length > 0) {
				nextItem.addClass("selected");
				selected.removeClass("selected");

				if (nextItem.offset().top + nextItem.height() > $(window).scrollTop() + viewport.height() - 100) {
					$(window).scrollTop($(window).scrollTop() + nextItem.height() + 100);
				}
			}
		}

		return false;
	});

	Mousetrap.bind('k', function() {
		if ($(".list .entries").length) {
			var selector = ".list .entries .entry";
			var type = "entry";
		} else if ($(".all .notebooks").length) {
			var selector = ".all .notebooks .notebook";
			var type = "notebook";
		} else {
			return;
		}

		// If nothing selected, select the first
		if ($(selector + ".selected").length == 0) {
			if (type == "entry") {
				$(selector + ":first-child").addClass("selected");
			} else if (type == "notebook") {
				$(".all .notebooks:first-child .notebook:first-child").addClass("selected");
			}
		} else {
			var selected = $(selector + ".selected");
			var prevItem = selected.prev();

			if (prevItem.length > 0) {
				prevItem.addClass("selected");
				selected.removeClass("selected");

				if (prevItem.offset().top < $(window).scrollTop()) {
					$(window).scrollTop($(window).scrollTop() - prevItem.height() - 80);
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

	// Go to entry/notebook
	Mousetrap.bind('return', function() {
		if ($(".entries .entry.selected").length > 0) {
			var entry = $(".entries .entry.selected");

			window.location.href = entry.attr("data-uri");

			return false;
		}

		// Go to notebook
		if ($(".notebooks .notebook.selected").length > 0) {
			var notebook = $(".notebooks .notebook.selected");

			window.location.href = notebook.attr("data-uri");

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
	// --------------------------------------------------

	$("input[name=tags]").tagit();


	// Autosave
	// --------------------------------------------------

	function autoSave(callback) {
		var currentBox = $("textarea[name=content]:visible");

		if (currentBox && currentBox.val()) {
			// Get updated stuff
			var currentText = currentBox.val().trim();
			var currentTitle = currentBox.siblings("input[name=title]");
			if (currentTitle) {
				currentTitle = currentTitle.val().trim();
			}
			var currentTags = currentBox.siblings(".edit-panel").find("input[name=tags]").val().trim();
			var currentDate = currentBox.siblings(".edit-panel").find("input[name=date]").val();
			var currentType = currentBox.siblings(".edit-panel").find("span.type.selected").attr("data-value");
			var currentNotebook = currentBox.siblings(".edit-panel").find("select[name=notebook]").val();

			// Originals
			var originalBox = currentBox.parents(".edit-mode").siblings(".original").find("textarea");
			var originalText = originalBox.val().trim();
			var originalTitle = originalBox.siblings("input[name=original_title]");
			if (originalTitle) {
				originalTitle = originalTitle.val().trim();
			}
			var originalTags = originalBox.siblings("input[name=original_tags]").val();
			if (typeof originalTags == 'undefined') {
				originalTags = '';
			}
			var originalDate = originalBox.siblings("input[name=original_date]").val();
			var originalType = originalBox.siblings("input[name=original_type]").val();
			var originalNotebook = originalBox.siblings("input[name=original_notebook]").val();

			var entry = currentBox.parents(".entry");
			var entryId = entry.attr("data-id");
			var notebookSlug = entry.attr("data-notebook-slug");

			var submit = false;
			var data = {};

			if (currentText != originalText) {
				data['content'] = currentText;
				submit = true;
			}

			if (currentTitle != originalTitle) {
				data['title'] = currentTitle;
				submit = true;
			}

			if (currentTags != originalTags) {
				if (currentTags == '' && originalTags != '') {
					data['tags'] = '[CLEAR]';
				} else {
					data['tags'] = currentTags;
				}
				submit = true;
			}

			if (currentDate != originalDate) {
				data['date'] = currentDate;
				submit = true;
			}

			if (currentType != originalType) {
				data['type'] = currentType;
				submit = true;
			}

			if (currentNotebook != originalNotebook) {
				data['notebook'] = currentNotebook;
				submit = true;
			}

			if (submit) {
				// Get an initial revision if it's not there
				var url = "/api/" + notebookSlug + "/" + entryId;
				if (!$("textarea[name=content]").attr("data-revision-id")) {
					// New revision for this session
					url += "/add-revision/";
				} else {
					// Update revision for this session
					var revisionId = $("textarea[name=content]").attr("data-revision-id");
					url += "/update-revision/" + revisionId + "/";
				}

				$.ajax({
					url: url,
					method: 'POST',
					contentType: 'application/json',
					data: JSON.stringify(data),
					success: function(data) {
						$(".dirty").removeClass("dirty");
						currentBox.attr("data-revision-id", data.revision_id);

						// Update current cache
						originalBox.html(currentText);

						if (currentTitle != originalTitle) {
							originalBox.siblings("input[name=original_title]").val(currentTitle);
						}

						if (currentTags != originalTags) {
							originalBox.siblings("input[name=original_tags]").val(currentTags);
						}

						if (currentDate != originalDate) {
							originalBox.siblings("input[name=original_date]").val(currentDate);
						}

						if (currentType != originalType) {
							originalBox.siblings("input[name=original_type]").val(currentType);
						}

						if (currentNotebook != originalNotebook) {
							originalBox.siblings("input[name=original_notebook]").val(currentNotebook);
						}

						// Update the returned HTML
						if (data.html) {
							entry.find(".content.container").html(data.html);
						}

						if (callback) {
							callback();
						}
					},
					error: function(data) {
						currentBox.addClass("error");
						_showError("Error autosaving", data);
					},
				});
			} else {
				currentBox.removeClass("dirty");
			}
		}
	}

	// Autosave any open add/edit boxes every 3 seconds
	var intervalId = window.setInterval(autoSave, 3000);

	// When the user types into the fields, make them slightly green
	// so it's clear that they're not saved
	$("textarea[name=content], input[name=title], input[name=tags], input[name=date]").on("input", function() {
		$(this).addClass("dirty");
	});

	$("li.tagit-new input[type=text]").on("input", function() {
		$("ul.tagit").addClass("dirty");
	});


	// Add notebook tray
	// --------------------------------------------------

	function _focusAddNotebookTray() {
		// Display and focus on the add notebook tray
		$("#add-notebook input[type=text]").val('');

		$("#add-notebook").slideDown(75, function() {
			$("#add-notebook input[type=text]").focus();
		});

		return false;
	}

	function _unfocusAddNotebookTray() {
		// Unfocus the add notebook tray
		$("#add-notebook").slideUp(75, function() {
			$("#add-notebook input[type=text]").val('').blur();
		});

		return false;
	}

	function _addNotebook() {
		var name = $("#add-notebook input[type=text]").val().trim();

		// Make sure there's a notebook name
		if (name == '') return false;

		var url = $("#add-notebook").attr("data-post-uri");
		var authorId = $("#add-notebook").attr("data-author-id");

		var data = {
			'name': name,
			'status': 'active',
			'author': authorId,
		};

		$.ajax({
			url: url,
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				// Go to the notebook page
				window.location.href = "/" + data.slug + "/";
				return true;
			},
			error: function(data) {
				_showError("Error adding notebook", data);
			},
		});

		return false;
	}

	Mousetrap.bind('A', _focusAddNotebookTray);
	var field = document.querySelector('#add-notebook input[type=text]');
	Mousetrap(field).bind('esc', _unfocusAddNotebookTray);
	Mousetrap(field).bind('mod+enter', _addNotebook);

	$("#add-notebook").submit(_addNotebook);


	// Editing notebooks
	// --------------------------------------------------

	// Edit notebook toggle

	$(".notebooks").on("click touchstart", ".notebook .controls-toggle", function() {
		var notebook = $(this).parents(".notebook");

		if (notebook.find(".edit-mode:visible").length > 0) {
			hideNotebookEditPanel(notebook);
		} else {
			showNotebookEditPanel(notebook);
		}

		return false;
	});

	function showNotebookEditPanel(notebook) {
		// Hide any other edit panels
		$(".notebooks .edit-mode:visible").fadeOut(150);

		// Show the edit area
		notebook.find(".edit-mode").fadeIn(150, function() {
			notebook.find(".edit-mode input[type=text]").focus();
		});

		notebook.find(".controls-toggle.active").removeClass("active");

		return false;
	}

	function hideNotebookEditPanel(notebook) {
		// Blur the input
		//notebook.find(".edit-mode input[type=text]").blur();

		// Hide the edit area
		notebook.find(".edit-mode").fadeOut(150);

		// Activate the toggle
		notebook.find(".controls-toggle.active").removeClass("active");

		return false;
	}


	// Add entry
	// --------------------------------------------------

	function _focusAddEntry() {
		// Display and focus on the add entry box
		$("#add-entry textarea").val('');

		$("#add-entry").slideDown(75, function() {
			autosize($("#add-entry textarea"));
			$("#add-entry textarea").focus();
		});

		return false;
	}

	function _unfocusAddEntry() {
		// Unfocus the add entry box
		$("#add-entry").slideUp(75, function() {
			$("#add-entry textarea").val('').blur();
		});

		return false;
	}

	function _addEntry() {
		var currentBox = $("textarea[name=entry-content]:visible");

		if (currentBox && currentBox.val()) {
			var currentText = currentBox.val().trim();
			var currentTitle = currentBox.siblings("input[name=title]");
			if (currentTitle) {
				currentTitle = currentTitle.val().trim();
			}
			var currentTags = currentBox.siblings(".edit-panel").find("input[name=tags]").val().trim();
			var currentDate = currentBox.siblings(".edit-panel").find("input[name=date]").val();
			var currentType = currentBox.siblings(".edit-panel").find("span.type.selected").attr("data-value");
			var currentNotebook = currentBox.siblings(".edit-panel").find("select[name=notebook]").val();

			// Originals
			var originalBox = currentBox.parents(".edit-mode").siblings(".original").find("textarea");
			var originalText = originalBox.val().trim();
			var originalTitle = originalBox.siblings("input[name=original_title]");
			if (originalTitle) {
				originalTitle = originalTitle.val().trim();
			}
			var originalTags = originalBox.siblings("input[name=original_tags]").val();
			if (typeof originalTags == 'undefined') {
				originalTags = '';
			}
			var originalDate = originalBox.siblings("input[name=original_date]").val();
			var originalType = originalBox.siblings("input[name=original_type]").val();
			var originalNotebook = originalBox.siblings("input[name=original_notebook]").val();

			var entry = currentBox.parents(".entry");
			var entryId = entry.attr("data-id");
			var notebookSlug = entry.attr("data-notebook-slug");

			var submit = false;
			var data = {};

			if (currentText != originalText) {
				data['content'] = currentText;
				submit = true;
			}

			if (currentTitle != originalTitle) {
				data['title'] = currentTitle;
				submit = true;
			}

			if (currentTags != originalTags) {
				if (currentTags == '' && originalTags != '') {
					data['tags'] = '[CLEAR]';
				} else {
					data['tags'] = currentTags;
				}
				submit = true;
			}

			if (currentDate != originalDate) {
				data['date'] = currentDate;
				submit = true;
			}

			if (currentType != originalType) {
				data['type'] = currentType;
				submit = true;
			}

			if (currentNotebook != originalNotebook) {
				data['notebook'] = currentNotebook;
				submit = true;
			}

			if (submit) {
				// Get an initial revision if it's not there
				var url = "/api/" + notebookSlug + "/" + entryId;
				if (!$("textarea[name=content]").attr("data-revision-id")) {
					// New revision for this session
					url += "/add-revision/";
				} else {
					// Update revision for this session
					var revisionId = $("textarea[name=content]").attr("data-revision-id");
					url += "/update-revision/" + revisionId + "/";
				}

				$.ajax({
					url: url,
					method: 'POST',
					contentType: 'application/json',
					data: JSON.stringify(data),
					success: function(data) {
						$(".dirty").removeClass("dirty");
						currentBox.attr("data-revision-id", data.revision_id);

						// Update current cache
						originalBox.html(currentText);

						if (currentTitle != originalTitle) {
							originalBox.siblings("input[name=original_title]").val(currentTitle);
						}

						if (currentTags != originalTags) {
							originalBox.siblings("input[name=original_tags]").val(currentTags);
						}

						if (currentDate != originalDate) {
							originalBox.siblings("input[name=original_date]").val(currentDate);
						}

						if (currentType != originalType) {
							originalBox.siblings("input[name=original_type]").val(currentType);
						}

						if (currentNotebook != originalNotebook) {
							originalBox.siblings("input[name=original_notebook]").val(currentNotebook);
						}

						// Update the returned HTML
						if (data.html) {
							entry.find(".content.container").html(data.html);
						}

						if (callback) {
							callback();
						}
					},
					error: function(data) {
						currentBox.addClass("error");
						_showError("Error autosaving", data);
					},
				});
			} else {
				currentBox.removeClass("dirty");
			}
		}
	}

	Mousetrap.bind('a', _focusAddEntry);
	var field = document.querySelector('#add-entry textarea');
	Mousetrap(field).bind('esc', _unfocusAddEntry);

	$("span.add-entry").on("click", function() {
		_hideMenu();
		_focusAddEntry();
	});


	// Menu items
	// --------------------------------------------------

	$("span.show-search").on("click", function() {
		_hideMenu();
		_focusSearch();
	});

	$("span.show-quickjump").on("click", function() {
		_hideMenu();
		_focusQuickJump();
	});

	$("span.add-notebook").on("click", function() {
		_hideMenu();
		_focusAddNotebookTray();
	});


	// Notebook settings page
	// --------------------------------------------------

	// Rename notebook

	$("#settings input[name=notebook-name]").on("input", function() {
		$(this).addClass("dirty");
	});

	$("#settings input.rename-notebook").on("click", function() {
		var field = $("#settings input[name=notebook-name]");
		var url = $("#settings").attr("data-uri");
		var value = field.val().trim();

		var data = {
			'name': value,
		};

		$.ajax({
			url: url,
			method: 'PUT',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				field.removeClass("dirty");
				$("#settings input.rename-notebook").blur();
			},
			error: function(data) {
				_showError("Error renaming notebook", data);
			},
		});
	});
	
	// Toggle sections

	$("#settings #section-config span.type").on("click", function() {
		var url = $("#settings").attr("data-uri");
		var button = $(this);

		var field = $(this).attr("data-field");
		var status = !$(this).hasClass("selected"); // Inverse

		var data = {};
		data[field] = status;

		$.ajax({
			url: url,
			method: 'PUT',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				// Toggle section
				button.toggleClass("selected");
			},
			error: function(data) {
				_showError("Error saving settings", data);
			},
		});
	});

	// Change default section

	$("#settings #default-section span.type").on("click", function() {
		var url = $("#settings").attr("data-uri");
		var button = $(this);

		var value = $(this).attr("data-value");
		var data = {
			'default_section': value,
		};

		$.ajax({
			url: url,
			method: 'PUT',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				// Change default section
				button.siblings(".selected").removeClass("selected");
				button.addClass("selected");
			},
			error: function(data) {
				_showError("Error saving settings", data);
			},
		});
	});

	// Notebook status changes

	$("#settings select#status").on("change", function() {
		var url = $("#settings").attr("data-uri");
		var value = $(this).val();

		var data = {
			'status': value,
		};

		$.ajax({
			url: url,
			method: 'PUT',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
			},
			error: function(data) {
				_showError("Error saving settings", data);
			},
		});
	});

	// Notebook group changes

	$("#settings select#group").on("change", function() {
		var url = $("#settings").attr("data-uri");
		var value = $(this).val();

		var data = {
			'group': value,
		};

		$.ajax({
			url: url,
			method: 'PUT',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
			},
			error: function(data) {
				_showError("Error saving settings", data);
			},
		});
	});


	// All Notebooks page
	// --------------------------------------------------

	// Rename notebook

	$(".notebooks .notebook span.rename-notebook").on("click", function() {
		var notebook = $(this).parents(".notebook");
		var url = notebook.attr("data-api-uri");
		var field = notebook.find("input[name=notebook-name]");
		var value = field.val().trim();

		var data = {
			'name': value,
		};

		$.ajax({
			url: url,
			method: 'PUT',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				notebook.find("h2.notebook-name").html(value);
				hideNotebookEditPanel(notebook);
			},
			error: function(data) {
				_showError("Error renaming notebook", data);
			},
		});
	});

	// Archive notebook

	$(".notebooks .notebook span.archive-notebook").on("click", function() {
		var notebook = $(this).parents(".notebook");
		var url = notebook.attr("data-api-uri");

		var data = {
			'status': 'archived',
		};

		$.ajax({
			url: url,
			method: 'PUT',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				hideNotebookEditPanel(notebook);
				notebook.slideUp(75);
			},
			error: function(data) {
				_showError("Error archiving notebook", data);
			},
		});
	});

	// Delete notebook

	$(".notebooks .notebook span.delete").on("click", function() {
		var notebook = $(this).parents(".notebook");
		var url = notebook.attr("data-api-uri");

		$.ajax({
			url: url,
			method: 'DELETE',
			contentType: 'application/json',
			success: function(data) {
				hideNotebookEditPanel(notebook);
				notebook.slideUp(75);
			},
			error: function(data) {
				_showError("Error deleting notebook", data);
			},
		});
	});


	/*
	// Save before closing tab
	$(window).bind('beforeunload', function() {
		// See if there's unsaved text and autosave if there is
		var currentText = $("textarea#text").val().trim();

		if (currentText != sceneText) {
			autoSave();

			confirm("Not done yet");
			// Delay a bit to let the autosave do its thing
			delay(500);
		}
	});
	*/
});

function processEntries(entries) {
	// Re-run Prism on all entries (old and new)
	// TODO: someday Prism.highlightElement might work, and then we can switch
	// to run it on only new entries, but for now it doesn't work
	Prism.highlightAll();
}
