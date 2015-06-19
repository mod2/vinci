// CSRF stuff

var autoSaveInProgress = false;

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

	$("#search .scope span").on("click", function() {
		$(this).siblings("span").removeClass("selected");
		$(this).addClass("selected");
	});


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
		} else {
			var scope = $("#search .scope span.selected").attr("data-value");
			var scopes = {
				'all': $("#search").attr("data-search-all-uri"),
				'notebook': $("#search").attr("data-search-notebook-uri"),
				'section': $("#search").attr("data-search-section-uri"),
			};

			var url = scopes[scope];
			var query = $("#search input[type=text]").val().trim();

			if (query.length > 0) {
				// Search
				var q = query.replace(/#(\w+)/g, 'tag:$1');

				url = url + '?q=' + q;
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
                beforeSend: function (request) {
                    request.setRequestHeader('X-API-KEY', config.api_key);
                },
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
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			if ($(e.target).hasClass("dirty")) {
				autoSave(true, function() {
					hideEditPanel($(e.target).parents(".entry"));
				});
			} else {
				hideEditPanel($(e.target).parents(".entry"));
			}

			return false;
		});
	}
	var fields = document.querySelectorAll(".edit-mode input.title");
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			if ($(e.target).hasClass("dirty")) {
				autoSave(true, function() {
					hideEditPanel($(e.target).parents(".entry"));
				});
			} else {
				hideEditPanel($(e.target).parents(".entry"));
			}

			return false;
		});
	}

	$(".edit-mode .group span.type").on("click", function() {
		var entryType = $(this).attr("data-value");
		if ($(this).parents("#add-entry").length > 0) {
			var parentEntry = $("#add-entry");
		} else {
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

	// Delete entry

	$(".entries").on("click touchstart", ".entry .buttons .button.delete", function() {
		if (confirm("Are you sure you want to delete this entry?")) {
			var entry = $(this).parents(".entry");
			var url = entry.attr("data-api-uri");

			$.ajax({
				url: url,
				method: 'DELETE',
				contentType: 'application/json',
				success: function(data) {
					hideEditPanel(entry);
					entry.slideUp(75).remove();
				},
				error: function(data) {
					_showError("Error deleting entry", data);
				},
			});
		}

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
			_hideModals();
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

	// Go to todo section
	Mousetrap.bind('g t', function() {
		var uri = $("#sections").attr("data-todo-uri");

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
		$("#modal-help").siblings(".modal").hide();
		$("#mask").fadeIn(200);
		$("#modal").fadeIn(200);
		$("#modal-help").fadeIn(200);
	}

	function _hideModals() {
		$("#modal .modal").fadeOut(200);
		$("#modal").fadeOut(200);
		$("#mask").fadeOut(200);
	}

	Mousetrap.bind('?', _showHelp);
	var modalForm = document.querySelector("#modal");
	Mousetrap(modalForm).bind('esc', _hideModals);

	// Hide modal on click mask
	$("#mask").on("click", function() {
		_hideModals();
	});


	// Tags
	// --------------------------------------------------

	$("input[name=tags]").tagit();


	// Autosave
	// --------------------------------------------------

	function autoSave(force, callback) {
		if (autoSaveInProgress && !force) {
			return;
		} else {
			autoSaveInProgress = true;
		}

		var currentBox = $("textarea[name=content]:visible");

		if ((currentBox && currentBox.val()) || force) {
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
			var url = entry.attr("data-api-uri");
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
				if (!$("textarea[name=content]").attr("data-revision-id")) {
					// New revision for this session
					url += "add-revision/";
				} else {
					// Update revision for this session
					var revisionId = $("textarea[name=content]").attr("data-revision-id");
					url += "update-revision/" + revisionId + "/";
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
							// Redirect to new page
							var newUrl = "/" + currentNotebook + "/" + currentType + "/" + entryId + "/";
							window.location.href = newUrl;
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
							if (currentType == 'page') {
								entry.find(".content.container .page-content").html(data.html);
							} else if (currentType == 'note') {
								// Do title differently
								var html = '<h3><a href="">' + data.first_line + '</a></h3>';
								if (data.second_line) {
									html += '<div class="second-line">' + data.second_line + '</div>';
								}
								entry.find(".content.container").html(html);
							} else {
								entry.find(".content.container").html(data.html);
							}
						}

						autoSaveInProgress = false;

						if (callback) {
							callback();
						}
					},
					error: function(data) {
						currentBox.addClass("error");
						_showError("Error autosaving", data);
						autoSaveInProgress = false;
					},
				});
			} else {
				currentBox.removeClass("dirty");
				autoSaveInProgress = false;
			}
		} else {
			autoSaveInProgress = false;
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
	Mousetrap(field).bind(['mod+enter', 'shift+enter'], _addNotebook);

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
		var currentBox = $("#add-entry textarea[name=entry-content]:visible");

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

			var data = {};

			if (currentText) {
				data['content'] = currentText;
			}

			if (currentTitle) {
				data['title'] = currentTitle;
			}

			if (currentTags) {
				data['tags'] = currentTags;
			}

			if (currentDate) {
				data['date'] = currentDate;
			}

			if (currentType) {
				data['type'] = currentType;
			}

			if (currentNotebook) {
				data['notebook'] = currentNotebook;
			}

			// Construct this manually because the notebook may have changed
			var url = "/api/" + currentNotebook + "/";

			$.ajax({
				url: url,
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					// Redirect to that notebook
					var newUrl = "/" + currentNotebook + "/" + currentType + "/";
					window.location.href = newUrl;
				},
				error: function(data) {
					_showError("Error adding entry", data);
				},
			});
		}

		return false;
	}

	Mousetrap.bind('a', _focusAddEntry);
	var field = document.querySelector('#add-entry textarea');
	Mousetrap(field).bind('esc', _unfocusAddEntry);
	Mousetrap(field).bind(['mod+enter', 'shift+enter'], _addEntry);
	$("#add-entry .add.button").on("click", _addEntry);

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

	// Toggle note section settings

	$("#settings #note-section-config span.type").on("click", function() {
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
		if (confirm("Are you sure you want to delete this notebook?")) {
			var notebook = $(this).parents(".notebook");
			var url = notebook.attr("data-api-uri");

			$.ajax({
				url: url,
				method: 'DELETE',
				contentType: 'application/json',
				success: function(data) {
					hideNotebookEditPanel(notebook);
					notebook.slideUp(75).remove();
				},
				error: function(data) {
					_showError("Error deleting notebook", data);
				},
			});
		}

		return false;
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

    // Login form
    // ----------------------------------------------------------
    $('#id_username').focus();


    // More shortcuts
    // ----------------------------------------------------------

	function _goToNotebookSettings() {
		var settingsUrl = $("main#content").attr("data-notebook-settings-url");

		if (settingsUrl) {
			window.location.href = settingsUrl;
		}

		return false;
	}

	Mousetrap.bind('g s', _goToNotebookSettings);


    // Todo mode
    // ----------------------------------------------------------

	resizeBoard();

	// Resize board on window resize
	$(window).resize(resizeBoard);

	makeListsSortable();
	makeCardsSortable();


	// Add card

	$(".lists").on("click", ".add-card .add-button", function() {
		var tray = $(this).siblings(".tray");
		var addButton = $(this);
		var inputBox = tray.find("textarea");

		if ($(this).siblings(".tray:visible").length) {
			_hideAddCardTray(tray);
		} else {
			addButton.html("Cancel");
			tray.slideDown(150, function() {
				inputBox.focus();
			});
		}
	});

	function _hideAddCardTray(tray) {
		var inputBox = tray.find("textarea");
		var addButton = tray.siblings(".add-button");
		addButton.html("Add card");
		tray.slideUp(150, function() {
			inputBox.val('');
		});
	}

	function _addCard(card) {
		var cardTitle = card.parents(".tray:first").find("textarea").val().trim();

		if (cardTitle != '') {
			var list = card.parents("section.list:first");
			var cardList = list.find("ul.cards");
			var url = cardList.attr("data-cards-uri");
			var listId = list.attr("data-list-id");
			var tray = list.find(".tray");

			var data = {
				list: listId,
				title: cardTitle,
				description: "",
				status: "active",
				order: 500,
				labels: [],
				mentions: [],
			};

			$.ajax({
				url: url,
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					var html = "<li class='card' style='display: none' data-card-id='" + data.id + "'>";
					html += "<span class='title no-desc'>" + cardTitle + "</span>";
					html += "</li>";
					cardList.append(html);
					cardList.find("li:last").slideDown(200);

					_updateCardOrderForList(cardList.parents("section.list:first"));

					_hideAddCardTray(tray);

					makeCardsSortable();
				},
				error: function(data) {
					_showError("Error adding card", data);
				},
			});
		}
	}

	$(".lists").on("click", ".add-card .save-button", function() {
		_addCard($(this));

		return false;
	});

	// Cmd+Enter (or Ctrl+Enter) to add a card
	var fields = document.querySelectorAll(".add-card textarea");
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			_addCard($(e.target));

			return false;
		});

		Mousetrap(fields[i]).bind('esc', function(e) {
			var tray = $(e.target).parents(".tray:first");
			_hideAddCardTray(tray);

			return false;
		});
	}


	// Add list

	$(".add-list").on("click", ".add-button", function() {
		var tray = $(this).siblings(".tray");
		var addButton = $(this);
		var inputBox = tray.find("textarea");

		if ($(this).siblings(".tray:visible").length) {
			_hideAddListTray(tray);
		} else {
			addButton.html("Cancel");
			tray.slideDown(150, function() {
				inputBox.focus();
			});
		}
	});

	function _hideAddListTray(tray) {
		var inputBox = tray.find("textarea");
		var addButton = tray.siblings(".add-button");
		addButton.html("Add list");
		tray.slideUp(150, function() {
			inputBox.val('');
		});
	}

	function _addList(list) {
		var listName = list.parents(".tray:first").find("textarea").val().trim();

		if (listName != '') {
			var addList = list.parents(".add-list");
			var url = $(".lists").attr("data-lists-uri");
			var notebookSlug = $(".lists").attr("data-notebook-slug");
			var tray = addList.find(".tray");

			var data = {
				notebook: notebookSlug,
				title: listName,
				status: "active",
				order: 100,
				labels: [],
			};

			$.ajax({
				url: url,
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					var html = "<section class='list' style='display: none' data-list-id='" + data.id + "' data-list-uri='" + data.url + "'>";
					html += "<h2 class='list-title'><span class='list-edit'>&hellip;</span><span class='title'>" + listName + "</span></h2>";
					html += "<ul class='cards'></ul>";
					html += "<section class='add-card'>";
					html += "<div class='tray'>";
					html += "<textarea></textarea>";
					html += "<span class='save-button'>Save card</span>";
					html += "</div>";
					html += "<span class='add-button'>Add card</span>";
					html += "</section>";

					addList.before(html);

					var newList = $(".lists .list:last");
					newList.fadeIn(200);

					_updateListOrder();

					resizeBoard();
					makeListsSortable();

					_hideAddListTray(tray);
				},
				error: function(data) {
					_showError("Error adding list", data);
				},
			});
		}
	}

	$(".add-list").on("click", ".save-button", function() {
		_addList($(this));

		return false;
	});

	// Cmd+Enter (or Ctrl+Enter) to add a list
	var fields = document.querySelectorAll(".add-list textarea");
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			_addList($(e.target));

			return false;
		});

		Mousetrap(fields[i]).bind('esc', function(e) {
			var tray = $(e.target).parents(".tray:first");
			_hideAddListTray(tray);

			return false;
		});
	}


	// Card edit modal

	$(".lists").on("click", "ul.cards .card", function() {
		// Show the modal
		$("#modal-card-edit").siblings(".modal").hide();
		$("#mask").fadeIn(200);
		$("#modal").fadeIn(200);
		$("#modal-card-edit").fadeIn(200);

		// Populate it with the card info
		var card = $(this);
		var cardTitle = card.find(".title").html();
		var cardDescription = card.find(".desc").html();
		$("#modal-card-edit #card-title-edit").val(cardTitle).focus();
		$("#modal-card-edit #card-description-edit").val(cardDescription);

		var cardURI = card.attr("data-card-uri");
		$("#modal-card-edit").attr("data-card-uri", cardURI);

		var cardId = card.attr("data-card-id");
		$("#modal-card-edit").attr("data-card-id", cardId);

		// Populate label info
		$("#modal-card-edit .label").removeClass("selected");
		card.find(".labels .label").each(function() {
			var labelId = $(this).attr("data-label-id");

			$("#modal-card-edit .label[data-label-id=" + labelId + "]").addClass("selected");
		});

		// Populate list name
		var listName = card.parents("section.list:first").find("h2.list-title .title").html();
		$("#modal-card-edit .card-edit .list-title").html(listName);

		// Populate checklists
		var checklistHtml = card.find(".checklistHtml").html();
		$("#modal-card-edit .checklists").html(checklistHtml);

		var fields = document.querySelectorAll('#modal-card-edit .add-checklist-item textarea');
		for (var i=0; i<fields.length; i++) {
			Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
				_addChecklistItem($(e.target));

				return false;
			});
		}

		var fields = document.querySelectorAll('#modal-card-edit .add-checklist textarea');
		for (var i=0; i<fields.length; i++) {
			Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
				_addChecklist($(e.target));

				return false;
			});
		}

		var fields = document.querySelectorAll('#modal-card-edit .label-edit');
		for (var i=0; i<fields.length; i++) {
			Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
				_saveChecklistItem($(e.target).parents(".checklist-item:first"));

				return false;
			});

			Mousetrap(fields[i]).bind('esc', function(e) {
				_hideChecklistItemEditTray($(e.target).parents(".checklist-item:first"));

				return false;
			});
		}

		// Make checklists sortable
		makeChecklistsSortable();
		makeChecklistItemsSortable();

		return false;
	});

	function _saveCardTitleDesc() {
		var modal = $("#modal-card-edit");
		var cardTitle = modal.find("textarea#card-title-edit").val().trim();
		var cardDescription = modal.find("textarea#card-description-edit").val().trim();

		if (cardTitle != '') {
			var url = modal.attr("data-card-uri");
			var cardId = modal.attr("data-card-id");
			var cardElement = $(".card[data-card-id=" + cardId + "]");

			var data = {
				title: cardTitle,
				description: cardDescription,
			};

			$.ajax({
				url: url,
				method: 'PATCH',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					// Update the card HTML
					cardElement.find(".title").html(cardTitle);

					if (cardDescription != '') {
						cardElement.find(".title").removeClass("no-desc");

						if (cardElement.find(".desc").length > 0) {
							cardElement.find(".desc").html(cardDescription);
						} else {
							$("<span class='desc'>" + cardDescription + "</span>").appendTo(cardElement);
						}
					} else {
						cardElement.find(".title").addClass("no-desc");
						cardElement.find(".desc").remove();
					}

					// Hide the modal
					_hideModals();
				},
				error: function(data) {
					_showError("Error editing card title/desc", data);
				},
			});
		}

		return false;
	}

	$("#modal-card-edit").on("click", "#save-card-edit-button", _saveCardTitleDesc);

	var fields = document.querySelectorAll('#modal-card-edit .card textarea');
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			_saveCardTitleDesc();

			return false;
		});
	}

	$("#modal-card-edit").on("click", "#cancel-card-edit-button", function() {
		_hideModals();
	});


	// Archive button for cards/lists

	$(".todo-edit").on("click", ".actions #card-archive-button, .actions #list-archive-button", function() {
		var modal = $(this).parents(".todo-edit:first");
		var editType = (modal.attr("id") == "modal-card-edit") ? "card" : "list";

		var url = modal.attr("data-" + editType + "-uri");
		var objId = modal.attr("data-" + editType + "-id");
		var objElement = $("." + editType + "[data-" + editType + "-id=" + objId + "]");

		var data = {
			status: 'archived',
		};

		$.ajax({
			url: url,
			method: 'PATCH',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				// Make the object disappear
				objElement.slideUp(200, function() {
					$(this).remove();
					_hideModals();
				});
			},
			error: function(data) {
				_showError("Error archiving card/list", data);
			},
		});
	});


	// Delete button for cards/lists

	$(".todo-edit").on("click", ".actions #card-delete-button, .actions #list-delete-button", function() {
		var modal = $(this).parents(".todo-edit:first");
		var editType = (modal.attr("id") == "modal-card-edit") ? "card" : "list";

		var url = modal.attr("data-" + editType + "-uri");
		var objId = modal.attr("data-" + editType + "-id");
		var objElement = $("." + editType + "[data-" + editType + "-id=" + objId + "]");

		var data = {
			status: 'deleted',
		};

		$.ajax({
			url: url,
			method: 'PATCH',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				// Make the object disappear
				objElement.slideUp(200, function() {
					$(this).remove();
					_hideModals();
				});
			},
			error: function(data) {
				_showError("Error deleting card/list", data);
			},
		});
	});


	// Edit card/list labels

	$(".todo-edit").on("click", ".labels li.label", function() {
		var label = $(this);

		// Toggle label class
		label.toggleClass("selected");

		var modal = $(this).parents(".todo-edit:first");
		var editType = (modal.attr("id") == "modal-card-edit") ? "card" : "list";
		var labelID = $(this).attr("data-label-id");

		var url = modal.attr("data-" + editType + "-uri");
		var objId = modal.attr("data-" + editType + "-id");
		var objElement = $("." + editType + "[data-" + editType + "-id=" + objId + "]");
		var labelsWrapper = objElement.find("> .labels");

		// Either way, we want the list of selected labels
		var labels = modal.find(".labels .label.selected");
		var labelList = [];
		for (var i=0; i<labels.length; i++) {
			labelList.push($(labels[i]).attr("data-label-id"));
		}

		var data = {
			labels: labelList,
		};

		$.ajax({
			url: url,
			method: 'PATCH',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				// Update the HTML

				if (labels.length > 0) {
					if (labelsWrapper.length == 0) {
						// Initialize the label list
						var html = "<span class='labels'>";
						for (var i=0; i<labels.length; i++) {
							var l = $(labels[i]);
							var id = l.attr("data-label-id");
							var color = l.attr("data-color");
							html += "<span class='label' data-label-id='" + id + "' data-color='" + color + "' style='background-color: " + color + ";'></span>";
						}
						html += "</span>";

						$(html).prependTo(objElement);
					} else {
						var html = "";
						for (var i=0; i<labels.length; i++) {
							var l = $(labels[i]);
							var id = l.attr("data-label-id");
							var color = l.attr("data-color");
							html += "<span class='label' data-label-id='" + id + "' data-color='" + color + "' style='background-color: " + color + ";'></span>";
						}

						labelsWrapper.html(html);
					}
				} else {
					// No labels
					labelsWrapper.remove();
				}
			},
			error: function(data) {
				_showError("Error editing card/list labels", data);
			},
		});
	});


	// List edit modal

	$(".lists").on("click", ".list-edit", function() {
		// Show the modal
		$("#modal-list-edit").siblings(".modal").hide();
		$("#mask").fadeIn(200);
		$("#modal").fadeIn(200);
		$("#modal-list-edit").fadeIn(200);

		// Populate it with the list info
		var list = $(this).parents("section.list:first");
		var listTitle = list.find(".title").html();
		$("#modal-list-edit #list-title-edit").val(listTitle).focus();

		var listURI = list.attr("data-list-uri");
		$("#modal-list-edit").attr("data-list-uri", listURI);

		var listId = list.attr("data-list-id");
		$("#modal-list-edit").attr("data-list-id", listId);

		// Populate label info
		$("#modal-list-edit .label").removeClass("selected");
		list.find("> .labels .label").each(function() {
			var labelId = $(this).attr("data-label-id");

			$("#modal-list-edit .label[data-label-id=" + labelId + "]").addClass("selected");
		});

		return false;
	});

	function _saveListTitle() {
		var modal = $("#modal-list-edit");
		var listTitle = modal.find("textarea#list-title-edit").val().trim();

		if (listTitle != '') {
			var url = modal.attr("data-list-uri");
			var listId = modal.attr("data-list-id");
			var listElement = $(".list[data-list-id=" + listId + "]");

			var data = {
				title: listTitle,
			};

			$.ajax({
				url: url,
				method: 'PATCH',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					// Update the list HTML
					listElement.find(".list-title .title").html(listTitle);

					// Hide the modal
					_hideModals();
				},
				error: function(data) {
					_showError("Error editing list title", data);
				},
			});
		}

		return false;
	}

	$("#modal-list-edit").on("click", "#save-list-edit-button", _saveListTitle);

	var fields = document.querySelectorAll('#modal-list-edit textarea');
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			_saveListTitle();

			return false;
		});
	}

	$("#modal-list-edit").on("click", "#cancel-list-edit-button", function() {
		_hideModals();
	});


	// Checklists

	function _checkItem(item) {
		item.toggleClass("checked");

		var done = item.hasClass("checked");
		var url = item.attr("data-checklist-item-uri");

		var data = {
			done: done,
		};

		$.ajax({
			url: url,
			method: 'PATCH',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
			},
			error: function(data) {
				_showError("Error checking item", data);
			},
		});
	}

	$(".todo-edit").on("click", ".checklist-item .checkbox", function() {
		_checkItem($(this).parents(".checklist-item:first"));
	});

	$(".todo-edit").on("click", ".checklist-item .label", function() {
		// Open checklist item edit area
		var labelEdit = $(this).siblings(".label-edit");
		var buttons = $(this).siblings(".save-item-button, .cancel-item-button");

		$(this).fadeOut(100, function() {
			labelEdit.fadeIn(100).focus();
			buttons.fadeIn(100);
		});

		return false;
	});

	function _hideChecklistItemEditTray(item) {
		// Hide checklist item edit area
		var label = item.find(".label");
		var items = item.find(".label-edit, .save-item-button, .cancel-item-button");

		items.fadeOut(100, function() {
			label.fadeIn(100);
		});
	}

	$(".todo-edit").on("click", ".checklist-item .cancel-item-button", function() {
		// Hide checklist item edit area
		_hideChecklistItemEditTray($(this).parents(".checklist-item:first"));

		return false;
	});

	function _hideAddChecklistItemTray(tray) {
		var inputBox = tray.find("textarea");
		var addButton = tray.siblings(".add-button");
		addButton.html("Add item");
		tray.slideUp(150, function() {
			inputBox.val('');
		});

		return false;
	}

	$(".checklists").on("click", ".add-checklist-item .add-button", function() {
		var tray = $(this).siblings(".tray");
		var addButton = $(this);
		var inputBox = tray.find("textarea");

		if ($(this).siblings(".tray:visible").length) {
			_hideAddChecklistItemTray(tray);
		} else {
			addButton.html("Cancel");
			tray.slideDown(150, function() {
				inputBox.focus();
			});
		}

		return false;
	});

	function _addChecklistItem(checklistItem) {
		var tray = checklistItem.parents(".tray:first");
		var itemTitle = tray.find("textarea").val().trim();

		if (itemTitle != '') {
			var modal = $("#modal-card-edit");
			var url = modal.attr("data-checklistitems-uri");
			var checklist = checklistItem.parents(".checklist:first");
			var checklistItems = checklist.find(".checklist-items");
			var checklistId = checklist.attr("data-checklist-id");

			var data = {
				title: itemTitle,
				status: "active",
				order: 500,
				done: false,
				checklist: checklistId,
			};

			$.ajax({
				url: url,
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					// Add checklist item to DOM

					var html = '<div class="checklist-item" data-checklist-item-id="' + data.id + '" data-checklist-item-uri="' + data.url + '" style="display: none;">';
					html += '<span class="checkbox"></span>';
					html += '<span class="label">' + itemTitle + '</span>';
					html += '<input type="text" class="label-edit" value="' + escape(itemTitle) + '" />';
					html += '<span class="save-item-button button">Save</span>';
					html += '<span class="cancel-item-button">&times;</span>';
					html += '</div>';

					checklistItems.append(html);
					checklistItems.find(".checklist-item:last").slideDown(200);

					_updateChecklistItemOrder(checklist);

					_hideAddChecklistItemTray(tray);

					makeChecklistItemsSortable();
				},
				error: function(data) {
					_showError("Error adding checklist item", data);
				},
			});
		}
	}

	$(".checklists").on("click", ".add-checklist-item .save-button", function() {
		_addChecklistItem($(this));

		return false;
	});


	$(".checklists-wrapper").on("click", ".add-checklist-button", function() {
		var modal = $("#modal-card-edit");
		var cardId = modal.attr("data-card-id");
		var url = modal.attr("data-checklists-uri");
		var checklistWrapper = modal.find(".checklists");

		var data = {
			title: "Checklist",
			status: "active",
			order: 500,
			card: cardId,
		};

		$.ajax({
			url: url,
			method: 'POST',
			contentType: 'application/json',
			data: JSON.stringify(data),
			success: function(data) {
				// Add checklist to DOM
				var html = '<div class="checklist ui-sortable" data-checklist-id="' + data.id + '" data-checklist-uri="' + data.url + '" style="display: none;">';
				html += '<span class="checklist-edit">&hellip;</span>';
				html += '<h2 class="checklist-title">Checklist</h2>';
				html += '<div class="checklist-items"></div>';
				html += '<div class="add-checklist-item">';
				html += '<div class="tray">';
				html += '<textarea></textarea>';
				html += '<span class="save-button button">Save item</span>';
				html += '</div>';
				html += '<span class="plus">+</span>';
				html += '<span class="add-button">Add item</span>';
				html += '</div>';
				html += '</div>';

				checklistWrapper.append(html);
				checklistWrapper.find(".checklist:last").slideDown(200);

				_updateChecklistOrder();
				makeChecklistsSortable();
			},
			error: function(data) {
				_showError("Error adding checklist", data);
			},
		});

		return false;
	});


	// Rename checklist items

	function _saveChecklistItem(item) {
		var newTitle = item.find(".label-edit").val().trim();

		if (newTitle != '') {
			var url = item.attr("data-checklist-item-uri");

			var data = {
				title: newTitle,
			};

			$.ajax({
				url: url,
				method: 'PATCH',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					// Update HTML
					item.find(".label").html(newTitle);

					_hideChecklistItemEditTray(item);
				},
				error: function(data) {
					_showError("Error renaming checklist item", data);
				},
			});
		}

		return false;
	}
	
	$(".checklists").on("click", ".checklist-item .save-item-button", function() {
		_saveChecklistItem($(this).parents(".checklist-item:first"));

		return false;
	});
});

function processEntries(entries) {
	// Re-run Prism on all entries (old and new)
	// TODO: someday Prism.highlightElement might work, and then we can switch
	// to run it on only new entries, but for now it doesn't work
	Prism.highlightAll();
}

function resizeBoard() {
	// Calculate total width (add one because of "Add list")
	var numLists = $(".lists .list").length + 1;

	$("#content .lists").css("width", "calc((" + numLists + " * 270px) + (" + (numLists - 1) + " * 15px))");

	// Calculate max-height (max-height: 100% doesn't work with flexbox for some reason)
	var height = $("#content .lists").height();
	$("#content .list").css("max-height", height);
}

function _updateListOrder() {
	var parentContainer = $(".lists");
	var url = parentContainer.attr("data-lists-uri");
	var order = {};

	// Get all the lists
	var items = parentContainer.find("section.list");

	for (var i=0; i<items.length; i++) {
		var item = $(items[i]);
		order[item.attr("data-list-id")] = i;
	}

	var data = {
		'operation': 'list-ordering',
		'list_orders': order,
	};

	$.ajax({
		url: url,
		method: 'PATCH',
		contentType: 'application/json',
		data: JSON.stringify(data),
		success: function(data) {
		},
		error: function(data) {
			console.log("Error! :(", data);
		},
	});
}

function makeListsSortable() {
	$(".lists").sortable({
		items: ".list",
		handle: "h2",
		placeholder: "list placeholder",
		forcePlaceholderSize: true,
		update: function(event, ui) {
			_updateListOrder();
		},
	});
}

function _updateCardOrderForList(list) {
	var list = list.find("ul.cards");
	var url = list.attr("data-list-uri");
	var order = {};

	// Get all the cards
	var items = list.find("li");

	for (var i=0; i<items.length; i++) {
		var item = $(items[i]);
		order[item.attr("data-card-id")] = i;
	}

	var data = {
		'operation': 'card-ordering',
		'card_orders': order,
	};

	$.ajax({
		url: url,
		method: 'PATCH',
		contentType: 'application/json',
		data: JSON.stringify(data),
		success: function(data) {
		},
		error: function(data) {
			console.log("Error! :(", data);
		},
	});
}

function makeCardsSortable() {
	$("ul.cards").sortable({
		placeholder: "card placeholder",
		items: "li",
		connectWith: "ul.cards",
		forcePlaceholderSize: true,
		update: function(event, ui) {
			var list = ui.item.parents("section.list:first");

			_updateCardOrderForList(list);
		},
	});
}

function makeChecklistsSortable() {
	$(".checklists").sortable({
		items: ".checklist",
		handle: "h2.checklist-title",
		placeholder: "placeholder",
		forcePlaceholderSize: true,
		update: function(event, ui) {
			// Update order
			_updateChecklistOrder();
		},
	});
}

function makeChecklistItemsSortable() {
	$(".checklist").sortable({
		items: ".checklist-item",
		handle: ".label",
		connectWith: ".checklist",
		placeholder: "placeholder",
		forcePlaceholderSize: true,
		update: function(event, ui) {
			// Update order
			var checklist = ui.item.parents(".checklist:first");

			_updateChecklistItemOrder(checklist);
		},
	});
}

function _updateChecklistOrder() {
	var checklists = $(".checklists");
	var url = $("#modal-card-edit").attr("data-checklists-uri");
	var order = {};

	// Get all the items
	var items = checklists.find(".checklist");

	for (var i=0; i<items.length; i++) {
		var item = $(items[i]);
		order[item.attr("data-checklist-id")] = i;
	}

	var data = {
		'operation': 'checklist-ordering',
		'checklist_orders': order,
	};

	$.ajax({
		url: url,
		method: 'PATCH',
		contentType: 'application/json',
		data: JSON.stringify(data),
		success: function(data) {
		},
		error: function(data) {
			console.log("Error! :(", data);
		},
	});
}

function _updateChecklistItemOrder(checklist) {
	var checklistWrapper = checklist.find(".checklist-items");
	var url = checklist.attr("data-checklist-uri");
	var order = {};

	// Get all the items
	var items = checklistWrapper.find(".checklist-item");

	for (var i=0; i<items.length; i++) {
		var item = $(items[i]);
		order[item.attr("data-checklist-item-id")] = i;
	}

	var data = {
		'operation': 'checklistitem-ordering',
		'checklistitem_orders': order,
	};

	$.ajax({
		url: url,
		method: 'PATCH',
		contentType: 'application/json',
		data: JSON.stringify(data),
		success: function(data) {
		},
		error: function(data) {
			console.log("Error! :(", data);
		},
	});
}

function setLabel(target, labelNum) {
	$(target).toggleClass("label-" + labelNum);
}

function getElement(e) {
	// TODO: this doesn't work yet
	var x = e.view.screenX;
	var y = e.view.screenY;

	return document.elementFromPoint(x, y);
}
