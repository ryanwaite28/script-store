// got from: https://stackoverflow.com/questions/523266/how-can-i-get-a-specific-parameter-from-location-search
var parseQueryString = function() {

	var str = window.location.search;
	var objURL = {};

	str.replace(
		new RegExp("([^?=&]+)(=([^&]*))?", "g"),
		function($0, $1, $2, $3) {
			objURL[$1] = $3;
		}
	);
	return objURL;
};

// got from: https://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript
function GeturlParams() {
	var match,
		pl = /\+/g, // Regex for replacing addition symbol with a space
		search = /([^&=]+)=?([^&]*)/g,
		decode = function(s) {
			return decodeURIComponent(s.replace(pl, " "));
		},
		query = window.location.search.substring(1);

	urlParams = {};
	while (match = search.exec(query))
		urlParams[decode(match[1])] = decode(match[2]);
}

// got from: https://davidwalsh.name/query-string-javascript
function getUrlParameter(name) {
	name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
	var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
	var results = regex.exec(location.search);
	return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

function getQueryVariable(variable) {
	var query = window.location.search.substring(1);
	var vars = query.split("&");
	for (var i = 0; i < vars.length; i++) {
		var pair = vars[i].split("=");
		if (pair[0] == variable) {
			return pair[1];
		}
	}
	return false;
}

// i made this
function get_url_params() {
	var query = {};
	var params = location.search.substr(1).split("&");
	params.forEach(param => {
		var splitter = param.split("=");
		var key = splitter[0];
		var value = splitter[1];
		query[key] = value;
	});
	return query;
}

function getParameterByName(name, url) {
	if (!url) {
		url = window.location.href;
	}
	name = name.replace(/[\[\]]/g, "\\$&");
	var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
		results = regex.exec(url);
	if (!results) return null;
	if (!results[2]) return '';
	return decodeURIComponent(results[2].replace(/\+/g, " "));
}
