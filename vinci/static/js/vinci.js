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

		xhr.setRequestHeader('X-API-KEY', config.api_key);
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
			$("#search .results").html('').hide();
		});

		return false;
	}

	$("#search .scope span").on("click", function() {
		$(this).siblings("span").removeClass("selected");
		$(this).addClass("selected");
	});


	// Keyboard shortcuts
	// --------------------------------------------------

	Mousetrap.bind('g m', _toggleMenu);

	Mousetrap.bind('/', _focusSearch);

	var field = document.querySelector('#search input[type=text]');
	Mousetrap(field).bind('esc', _unfocusSearch);

	$("#search").on('submit', _executeSearch);

	function _executeSearch() {
		var url = '';

		if ($("#search .results a").length > 0) {
			// Go to the first one
			var result = $("#search .results a:first-child");
			var url = result.attr("href");
		} else {
			var url = $("#search").attr("data-search-section-uri");
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
	$("#page").on("input", "#search", function() {
		// On typing, call the API
		var url = $("#search").attr("data-quickjump-uri");
		var query = $("#search input[type=text]").val().trim();

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

					for (var i in data.results.sections) {
						var s = data.results.sections[i];

						html += '<a class="section" href="' + s.url + '" data-slug="' + s.slug + '">' + s.name + '</a>';
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
			// Hide results
			$("#search .results").html('').hide();
		}
	});


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
	}

	// Cmd+Enter (or Ctrl+Enter) to save and close an entry
	var fields = document.querySelectorAll(".edit-mode textarea");
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			// Save the contents
			save(function() {
				hideEditPanel($(e.target).parents(".entry"));
			});

			return false;
		});
	}
	var fields = document.querySelectorAll(".edit-mode input[type=text]");
	for (var i=0; i<fields.length; i++) {
		Mousetrap(fields[i]).bind(['mod+enter', 'shift+enter'], function(e) {
			// Save the contents
			save(function() {
				hideEditPanel($(e.target).parents(".entry"));
			});

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

	// Save entry

	$(".edit-mode .group.more a.save").on("click", function(e) {
		save(function() {
			hideEditPanel($(e.target).parents(".entry"));
		});

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


	// Save entry
	// --------------------------------------------------

	function save(callback) {
		var currentBox = $("textarea[name=content]:visible");

		if (currentBox && currentBox.val()) {
			var currentText = currentBox.val().trim();
			var entry = currentBox.parents(".entry");
			var entryId = entry.attr("data-id");
			var url = $(".entries").attr("data-uri");
			var notebookSlug = entry.attr("data-notebook-slug");

			var submit = false;
			var data = {
				'content': currentText,
			};

			$.ajax({
				url: url,
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
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
					_showError("Error saving", data);
				},
			});
		}
	}


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
		var currentNotebook = $("#add-entry").attr("data-notebook-slug");
		var currentSection = $("#add-entry").attr("data-section-slug");

		if (currentBox && currentBox.val()) {
			var currentText = currentBox.val().trim();
			var url = $("#add-entry").attr("data-uri");
			var data = {};

			if (currentText) data['content'] = currentText;
			if (currentNotebook) data['notebook'] = currentNotebook;
			if (currentSection) data['section'] = currentSection;

			$.ajax({
				url: url,
				method: 'POST',
				contentType: 'application/json',
				data: JSON.stringify(data),
				success: function(data) {
					window.location.reload();
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
	$("#add-entry .add").on("click", _addEntry);

	$("span.add-entry").on("click", function() {
		if ($("#add-entry:visible").length > 0) {
			_unfocusAddEntry();
		} else {
			_focusAddEntry();
		}
	});


	// Menu items
	// --------------------------------------------------

	$("span.show-search").on("click", function() {
		if ($("#search:visible").length > 0) {
			_unfocusSearch();
		} else {
			_focusSearch();
		}
	});

	$("span.add-notebook").on("click", function() {
		_hideMenu();
		_focusAddNotebookTray();
	});


	// Notebook settings page
	// --------------------------------------------------

	// Rename notebook

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
				$("#settings input.rename-notebook").blur();
			},
			error: function(data) {
				_showError("Error renaming notebook", data);
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
			save();

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

	// Revision display toggle
	$("ul.revisions li a.toggle").on("click", function() {
		$(this).parents("ul.revisions").toggleClass("show");

		return false;
	});
});

function processEntries(entries) {
	// Re-run Prism on all entries (old and new)
	// TODO: someday Prism.highlightElement might work, and then we can switch
	// to run it on only new entries, but for now it doesn't work
	Prism.highlightAll();
}
