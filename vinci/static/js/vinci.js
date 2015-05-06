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
});
